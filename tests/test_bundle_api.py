"""HTTP contract checks against the real app, using only stdlib HTTP tools."""
from io import StringIO
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
from app.profiles.lpbf import PROFILE
COLUMNS = {key: PROFILE[key] for key in ("subgroup_col", "order_col", "value_col")}
from app.qc import analyze

ROOT = Path(__file__).resolve().parents[1]
KNOWN = 'build_id,build_date,uts_mpa\n' + ''.join(
    f'B{i},2026-01-0{i},{value}\n'
    for i, values in enumerate(((990, 1000, 1010), (1005, 1010, 1015),
                                (975, 990, 1005), (990, 1000, 1010)), 1)
    for value in values)


class ApiChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        cls.base = f'http://127.0.0.1:{port}'
        cls.log = tempfile.TemporaryFile()
        cls.process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.app:app',
                                        '--host', '127.0.0.1', '--port', str(port)],
                                       cwd=ROOT, stdout=cls.log, stderr=cls.log)
        cls.addClassCleanup(cls.stop_server)
        for _ in range(100):
            try:
                with urlopen(cls.base + '/health', timeout=1):
                    return
            except (URLError, OSError):
                if cls.process.poll() is not None:
                    cls.log.seek(0)
                    raise RuntimeError(cls.log.read().decode())
                time.sleep(0.1)
        raise RuntimeError('API did not become ready')

    @classmethod
    def stop_server(cls):
        cls.process.terminate()
        try:
            cls.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.process.kill()
            cls.process.wait()
        cls.log.close()

    def request(self, route, data=None, headers=None):
        try:
            with urlopen(Request(self.base + route, data=data, headers=headers or {}), timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def upload(self, csv, lsl='980', settings=None):
        boundary = 'aeroqual-api-test'
        values = {'lsl': lsl, **(settings or {})}
        parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'
                 for name, value in values.items()]
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.csv"\r\nContent-Type: text/csv\r\n\r\n{csv}\r\n--{boundary}--\r\n')
        return self.request('/analyze', ''.join(parts).encode(),
                            {'Content-Type': 'multipart/form-data; boundary=' + boundary})

    def test_health_and_dataset_listing(self):
        self.assertEqual(self.request('/health')[1]['status'], 'ok')
        status, payload = self.request('/datasets')
        self.assertEqual(status, 200)
        self.assertEqual(payload['datasets'], sorted(path.stem for path in (ROOT / 'data').glob('*.csv')))

    def test_known_answer_upload_matches_every_core_field(self):
        status, result = self.upload(KNOWN)
        self.assertEqual(status, 200)
        expected = analyze(pd.read_csv(StringIO(KNOWN)), 980, **COLUMNS)
        self.assertEqual({key: result[key] for key in expected}, expected)
        self.assertAlmostEqual(result['cpk'], 0.5908179503018387)
        self.assertEqual(sum(bin['count'] for bin in result['histogram']), 12)

    def test_all_named_datasets_match_upload_and_core(self):
        for path in sorted((ROOT / 'data').glob('*.csv')):
            with self.subTest(dataset=path.name):
                status, named = self.request(f'/analyze?dataset={path.stem}&lsl=895')
                self.assertEqual(status, 200)
                status, uploaded = self.upload(path.read_text(), '895')
                self.assertEqual(status, 200)
                self.assertEqual(named, uploaded)
                expected = analyze(pd.read_csv(path), 895, **COLUMNS)
                self.assertEqual({key: named[key] for key in expected}, expected)

    def test_constant_data_and_settings(self):
        frame = pd.read_csv(StringIO(KNOWN))
        frame['uts_mpa'] = 1000
        status, result = self.upload(frame.to_csv(index=False))
        self.assertEqual(status, 200)
        self.assertIsNone(result['cpk'])
        self.assertIsNone(result['ppk'])
        self.assertIn('no variation', result['reason'])
        status, result = self.upload(KNOWN, settings={'min_builds': '4'})
        self.assertEqual(status, 200)
        self.assertEqual(result['verdict'], 'not capable')

    def test_bad_input_returns_clear_errors(self):
        for content, message in [('wrong\n1\n', 'missing column'),
                                 (KNOWN.replace('990\n', '\n', 1), 'row 0')]:
            with self.subTest(message=message):
                status, error = self.upload(content)
                self.assertEqual(status, 400)
                self.assertIn(message, error['detail'])
        self.assertEqual(self.upload(KNOWN, 'nan')[0], 400)
        self.assertEqual(self.request('/analyze?dataset=../SPEC.md&lsl=895')[0], 404)

    def test_optional_context_matches_observed_unflagged_ranges(self):
        _, result = self.request('/analyze?dataset=unstable_shift&lsl=895')
        frame = pd.read_csv(ROOT / 'data/unstable_shift.csv')
        flags = {build['build_id'] for build in result['builds'] if build['flagged']}
        params = result['parameters']
        for column in params['columns']:
            per_build = frame.groupby('build_id')[column].mean()
            reference = per_build.drop(index=list(flags))
            self.assertEqual(params['usual_range'][column]['min'], float(reference.min()))
            self.assertEqual(params['usual_range'][column]['max'], float(reference.max()))
        self.assertEqual({build['build_id'] for build in params['flagged_builds']}, flags)


if __name__ == '__main__':
    unittest.main()
