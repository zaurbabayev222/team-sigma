"""Generate an offline engineering brief from the actual FastAPI upload endpoint.

Run from the repository root: python demo/brief_source/build_brief.py --capture
Then verify without any API server: python demo/brief_source/build_brief.py --check
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    import pandas as pd
    from fastapi.testclient import TestClient
    from app.app import app
    from app.profiles import DATASETS, PROFILES
    from app.qc import analyze
    from demo.check import compare

    sources = [ROOT / 'app' / name for name in
               ('app.py', 'qc.py', 'signals.py', 'inspection.py', 'investigation.py', 'pareto_view.py')]
    sources += sorted((ROOT / 'app/profiles').glob('*.py'))
    sources += sorted((ROOT / 'data').glob('*.csv'))
    # Snapshot attribution must refer to committed analysis/data, not a stale server process.
    for path in sources:
        name = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == sha(path), f'Uncommitted analysis/data: {name}'
    cases = []
    with TestClient(app) as client:
        for process, names in DATASETS.items():
            for index, name in enumerate(names):
                path = ROOT / 'data' / (name + '.csv')
                response = client.post('/analyze', data={'lsl':895, 'process_type':process},
                                       files={'file':(path.name, path.read_bytes(), 'text/csv')})
                response.raise_for_status()
                result = response.json()
                frame = pd.read_csv(path, converters={'primary_defect':str})
                core = analyze(frame,895,subgroup_col='build_id',order_col='build_date',value_col='uts_mpa')
                compare(core, result)
                # Source records are traceability, not a second analysis or aggregation.
                records = json.loads(frame.to_json(orient='records'))
                cases.append(dict(process=process, scenario=index, dataset=name, sha256=sha(path),
                                  records=records, result=result))
    data = dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                origin_main=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),
                captured_at=datetime.now(timezone.utc).isoformat(), lsl=895, min_builds=25, cpk_target=1.33,
                mode='Offline snapshot from FastAPI POST /analyze via in-process TestClient; synthetic inputs only.',
                profiles=list(PROFILES.values()), cases=cases,
                hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    (HERE / 'snapshot.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print('PASS: 16 actual FastAPI responses; all core fields match Python; committed source/data attribution verified')


def build(check, dashboard_url):
    data = json.loads((HERE / 'snapshot.json').read_text(encoding='utf-8'))
    for name, value in data['hashes'].items():
        assert sha(ROOT / name) == value, f'Stale snapshot: {name}'
    assert dashboard_url.startswith(('http://','https://')), 'Dashboard URL must be HTTP(S)'
    data['dashboard_url'] = dashboard_url
    text = (HERE / 'brief.template.html').read_text(encoding='utf-8')
    font = base64.b64encode((HERE/'fonts/IBMPlexSans-Medium.woff2').read_bytes()).decode('ascii')
    css = (HERE/'brief.css').read_text(encoding='utf-8').replace('@@FONT@@',font)
    license_text = (HERE/'fonts/LICENSE.txt').read_text(encoding='utf-8')
    text = text.replace('<!doctype html>', '<!doctype html>\n<!-- Embedded IBM Plex Sans font license:\n' + license_text + '\n-->')
    for key, value in {'@@CSS@@':css,
                       '@@JS@@':(HERE/'brief.js').read_text(encoding='utf-8'),
                       '@@DATA@@':json.dumps(data,ensure_ascii=True).replace('<','\\u003c')}.items():
        text = text.replace(key,value)
    artifact = ROOT / 'demo/aeroqual_brief.html'
    if check:
        assert artifact.read_text(encoding='utf-8') == text, 'Rebuild stale HTML artifact'
        print('PASS: self-contained engineering brief matches snapshot, source hashes and templates')
    else:
        artifact.write_text(text,encoding='utf-8',newline='\n')
        print('Built demo/aeroqual_brief.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--dashboard-url',default='https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/dashboard/')
    args = parser.parse_args()
    if args.capture:
        capture()
    build(args.check,args.dashboard_url)
