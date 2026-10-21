"""Verify unauthenticated dashboard/API behavior, locally or after deployment."""
import argparse
from contextlib import contextmanager
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def read(base, route, **kwargs):
    request = Request(urljoin(base.rstrip('/') + '/', route), **kwargs)
    with urlopen(request, timeout=15) as response:
        return response.headers.get('Content-Type', ''), response.read()


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('src'):
            self.paths.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet' and attrs.get('href'):
            self.paths.append(attrs['href'])


def check(base):
    content_type, html = read(base, 'dashboard/')
    if 'text/html' not in content_type or b'<html' not in html.lower():
        raise ValueError('Dashboard route must return HTML')
    assets = Assets()
    assets.feed(html.decode('utf-8'))
    if not assets.paths:
        raise ValueError('Dashboard HTML must load its built frontend assets')
    for asset in assets.paths:
        content_type, contents = read(base, urljoin('dashboard/', asset))
        if not contents or not any(kind in content_type for kind in ('javascript', 'text/css')):
            raise ValueError('Dashboard JavaScript/CSS did not load')
    content_type, payload = read(base, 'health')
    if 'json' not in content_type or json.loads(payload).get('status') != 'ok':
        raise ValueError('Public health route must return JSON status=ok')
    # SPEC section 4 illustrative arithmetic, generated in memory only.
    rows = ['build_id,build_date,uts_mpa']
    for i, values in enumerate(((990, 1000, 1010), (1005, 1010, 1015),
                                (975, 990, 1005), (990, 1000, 1010)), 1):
        rows.extend(f'B{i},2026-01-0{i},{value}' for value in values)
    boundary = 'aeroqual-known-answer'
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="lsl"\r\n\r\n980\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="known.csv"\r\n'
            'Content-Type: text/csv\r\n\r\n' + '\n'.join(rows) + f'\r\n--{boundary}--\r\n').encode()
    _, payload = read(base, 'analyze', data=body,
                      headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
    result = json.loads(payload)
    expected = {'cpk': 0.591, 'ppk': 0.571, 'failure_rate': 1 / 12,
                'sigma_short': 11.284, 'sigma_total': 11.677}
    for key, value in expected.items():
        if not math.isclose(result[key], value, abs_tol=0.001):
            raise ValueError('Known-answer mismatch: ' + key)
    if result['n_builds'] != 4 or result['n_coupons'] != 12 or result['n_failures'] != 1:
        raise ValueError('Known-answer subgroup/coupon counts differ')
    if result['verdict'] != 'not assessable' or 'too few' not in result['reason'].lower():
        raise ValueError('Known-answer assessment reason differs')
    for key, value in [('center', 1000), ('lcl', 980.46), ('ucl', 1019.54)]:
        if not math.isclose(result['xbar'][key], value, abs_tol=0.01):
            raise ValueError('Known-answer X-bar limits differ')
    for key, value in [('center', 10), ('lcl', 0), ('ucl', 25.68)]:
        if not math.isclose(result['s_chart'][key], value, abs_tol=0.01):
            raise ValueError('Known-answer S limits differ')
    if any(build['flagged'] for build in result['builds']):
        raise ValueError('Known-answer builds must not be flagged')
    print('PASS: public HTML dashboard and assets, JSON health, X-bar/S limits and SPEC known-answer upload')
    print('Cpk=0.591; Ppk=0.571; failures=1/12; verdict=not assessable (too few builds)')


@contextmanager
def local_server(bundle):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app',
                                    '--host', '127.0.0.1', '--port', str(port)],
                                   cwd=bundle, stdout=log, stderr=log)
        try:
            yield f'http://127.0.0.1:{port}/'
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def retry(base, attempts):
    for attempt in range(attempts):
        try:
            check(base)
            return
        except (HTTPError, URLError, ValueError, KeyError, TypeError, OSError):
            if attempt + 1 == attempts:
                raise ValueError('Public dashboard/API verification failed; inspect app logs and access settings') from None
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--bundle', type=Path)
    source.add_argument('--url-env', help='Environment variable holding the content URL; never prints it')
    parser.add_argument('--attempts', type=int, default=20)
    args = parser.parse_args()
    try:
        if args.attempts < 1 or args.attempts > 20:
            raise ValueError('Use between 1 and 20 attempts')
        if args.bundle:
            if not (args.bundle / 'app.py').is_file():
                raise ValueError('Missing H-04 API in prepared bundle')
            with local_server(args.bundle.resolve()) as base:
                retry(base, args.attempts)
                checker = Path(__file__).resolve().parents[2] / 'demo/check.py'
                subprocess.run([sys.executable, str(checker), '--base-url', base], check=True)
        else:
            base = os.environ.get(args.url_env, '')
            if not base.startswith('https://'):
                raise ValueError('Content URL must be provided through the named environment variable using HTTPS')
            retry(base, args.attempts)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'ERROR: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
