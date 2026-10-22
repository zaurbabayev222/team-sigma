"""Capture verified local API outputs and build an offline, dependency-free lesson deck."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'demo'
sys.path.insert(0, str(ROOT))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(base_url):
    import pandas as pd
    from app.profiles import DATASETS
    from app.qc import analyze
    from demo.check import compare

    def get(process, dataset, lsl=895, **filters):
        query = urlencode(dict(process_type=process, dataset=dataset, lsl=lsl, **filters))
        with urlopen(base_url.rstrip('/') + '/analyze?' + query, timeout=30) as response:
            result = json.load(response)
        core = analyze(pd.read_csv(ROOT / 'data' / (dataset + '.csv')), lsl,
                       subgroup_col='build_id', order_col='build_date', value_col='uts_mpa')
        compare(core, result)
        return result

    sources = ['app/qc.py', 'app/app.py', 'app/signals.py', 'app/inspection.py',
               'app/investigation.py', 'app/pareto_view.py']
    sources.extend(str(p.relative_to(ROOT)).replace('\\', '/')
                   for p in sorted((ROOT / 'app/profiles').glob('*.py')))
    cases = []
    for process, datasets in DATASETS.items():
        for name in datasets:
            path = ROOT / 'data' / (name + '.csv')
            sources.append(str(path.relative_to(ROOT)).replace('\\', '/'))
            cases.append(dict(process=process, dataset=name, csv=path.read_bytes().decode('utf-8'),
                              sha256=digest(path), result=get(process, name)))
    experiments = {p: {str(lsl): get(p, names[0], lsl) for lsl in (895, 925, 980)}
                   for p, names in DATASETS.items()}
    windows = {'all': {}, 'single': dict(start_date='2026-10-24', end_date='2026-10-24'),
               'range': dict(start_date='2026-10-20', end_date='2026-10-25'),
               'empty': dict(start_date='2027-01-01', end_date='2027-01-31')}
    views = {key: get('laser_ded', 'laser_ded_inspection_demo', **filters)
             for key, filters in windows.items()}
    snapshot = dict(captured_at=datetime.now(timezone.utc).isoformat(),
                    revision=subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip(),
                    provenance='Local working tree, including uncommitted candidate changes; synthetic data only; not a deployment.',
                    source_hashes={name: digest(ROOT / name) for name in sources},
                    cases=cases, experiments=experiments, views=views)
    (HERE / 'deck-data.json').write_text(json.dumps(snapshot, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(f'Captured {len(cases)} scenarios, 12 requirement experiments and four date views; API/core parity PASS')


def build(check=False):
    data_path = HERE / 'deck-data.json'
    data = json.loads(data_path.read_text(encoding='utf-8'))
    for name, expected in data['source_hashes'].items():
        assert digest(ROOT / name) == expected, f'Stale capture: {name}; recapture the running current API'
    html = (HERE / 'slidedeck.template.html').read_text(encoding='utf-8')
    for marker, content in {
        '@@CSS@@': (HERE / 'slidedeck.css').read_text(encoding='utf-8'),
        '@@DATA@@': json.dumps(data, ensure_ascii=True).replace('<', '\\u003c'),
        '@@JS@@': (HERE / 'slidedeck.js').read_text(encoding='utf-8'),
    }.items():
        html = html.replace(marker, content)
    target = HERE / 'slidedeck' / 'index.html'
    if check:
        assert target.read_text(encoding='utf-8') == html, 'Deck is stale: run python demo/build_slidedeck.py'
        print('Offline deck matches sources and captured API/data hashes: PASS')
    else:
        target.parent.mkdir(exist_ok=True)
        target.write_text(html, encoding='utf-8', newline='\n')
        print('Built demo/slidedeck/index.html (self-contained)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--base-url', default='http://127.0.0.1:8001')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.capture:
        capture(args.base_url)
    build(args.check)
