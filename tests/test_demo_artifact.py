"""Keep offline tutorial evidence synchronized with the actual source datasets."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_offline_artifact_is_current():
    subprocess.run([sys.executable, str(ROOT / 'demo/build_slidedeck.py'), '--check'], check=True)


def test_downloads_are_exact_sources_and_all_scenarios_present():
    data = json.loads((ROOT / 'demo/deck-data.json').read_text(encoding='utf-8'))
    assert len(data['cases']) == 16
    assert {c['process'] for c in data['cases']} == {'lpbf', 'waam', 'ebpbf', 'laser_ded'}
    for case in data['cases']:
        source = (ROOT / 'data' / (case['dataset'] + '.csv')).read_bytes()
        assert case['csv'].encode('utf-8') == source
        assert hashlib.sha256(source).hexdigest() == case['sha256']
        assert case['result']['n_builds'] == 30
        assert case['result']['n_coupons'] == 90


def test_experiments_and_views_preserve_the_control_baseline():
    data = json.loads((ROOT / 'demo/deck-data.json').read_text(encoding='utf-8'))
    for choices in data['experiments'].values():
        base = choices['895']
        for result in choices.values():
            assert result['builds'] == base['builds']
            assert result['xbar'] == base['xbar']
            assert result['s_chart'] == base['s_chart']
        assert choices['980']['n_failures'] >= base['n_failures']
        assert choices['980']['cpk'] < base['cpk']
    base = data['views']['all']
    for view in data['views'].values():
        for key in ['cpk', 'ppk', 'xbar', 's_chart', 'verdict', 'n_failures']:
            assert view[key] == base[key]
    single = data['views']['single']['investigation_view']
    assert single['window_builds'] == 1
    assert single['signal_pareto']['total_signals'] == 2
    assert single['signal_pareto']['flagged_builds'] == 1
    assert data['views']['empty']['investigation_view']['window_builds'] == 0
