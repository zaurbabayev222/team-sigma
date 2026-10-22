"""Verify the new brief's provenance, actual numbers and reproducible standalone artifact."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd

from app.qc import analyze
from demo.check import compare

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'demo/brief_source'


def test_engineering_brief_rebuild_is_exact_and_sources_are_current():
    subprocess.run([sys.executable,str(SOURCE/'build_brief.py'),'--check'],check=True,cwd=ROOT)


def test_every_snapshot_matches_repository_core_and_data():
    data = json.loads((SOURCE/'snapshot.json').read_text(encoding='utf-8'))
    assert len(data['revision']) == 40
    assert len(data['cases']) == 16
    assert {p['name'] for p in data['profiles']} == {'lpbf','waam','ebpbf','laser_ded'}
    for case in data['cases']:
        path = ROOT/'data'/(case['dataset']+'.csv')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == case['sha256']
        frame = pd.read_csv(path,converters={'primary_defect':str})
        compare(analyze(frame,data['lsl'],'build_id','build_date','uts_mpa'),case['result'])
        assert len(case['records']) == case['result']['n_coupons'] == 90
        assert sum(b['count'] for b in case['result']['histogram']) == 90
        assert case['result']['profile']['name'] == case['process']
        if case['scenario'] in (2,3):
            assert case['result']['verdict'] == 'not assessable'
        assert [row['uts_mpa'] for row in case['records']] == frame.uts_mpa.tolist()


def test_offline_artifact_embeds_snapshot_without_external_runtime():
    html = (ROOT/'demo/aeroqual_brief.html').read_text(encoding='utf-8')
    assert 'src="http' not in html and '<link rel="stylesheet"' not in html
    assert '@@CSS@@' not in html and '@@JS@@' not in html and '@@DATA@@' not in html
    assert '<script id="brief-data" type="application/json">' in html
    # Explicitly prevent a presentation change from turning the artifact into a second API/statistics client.
    js = (SOURCE/'brief.js').read_text(encoding='utf-8')
    assert 'fetch(' not in js and 'XMLHttpRequest' not in js
    assert 'Capability withheld' in js and 'descriptive only' in js
