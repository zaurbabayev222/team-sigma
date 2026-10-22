from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.profiles import DATASETS, PROFILES
from app.qc import analyze
from app.signals import signal_pareto
from data.validate_additional import validate

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_additional_datasets_independently_validate():
    validate()


@pytest.mark.parametrize('process', ['ebpbf', 'laser_ded'])
def test_all_new_named_and_upload_scenarios_preserve_the_core(process):
    names = client.get('/datasets', params={'process_type': process}).json()['datasets']
    assert names == sorted(DATASETS[process]) and len(names) == 4
    for name in names:
        path = ROOT / 'data' / (name + '.csv')
        core = analyze(pd.read_csv(path), 895, 'build_id', 'build_date', 'uts_mpa')
        named = client.get('/analyze', params={'process_type':process,'dataset':name,'lsl':895})
        assert named.status_code == 200
        result = named.json()
        uploaded = client.post('/analyze', data={'process_type':process,'lsl':895}, files={'file':(path.name,path.read_bytes(),'text/csv')})
        assert uploaded.status_code == 200 and uploaded.json() == result
        assert {k:result[k] for k in core} == core
        assert result['signal_pareto'] == signal_pareto(core)
        assert result['profile']['parameters'] == PROFILES[process]['parameters']
        assert result['investigation_actions']


def test_all_process_pair_mismatches_reject_and_shared_columns_are_allowed():
    for selected in PROFILES:
        for actual, names in DATASETS.items():
            if selected == actual:
                continue
            path = ROOT/'data'/(names[0]+'.csv')
            assert client.get('/analyze',params={'process_type':selected,'dataset':names[0],'lsl':895}).status_code == 404
            response = client.post('/analyze',data={'process_type':selected,'lsl':895},files={'file':(path.name,path.read_bytes(),'text/csv')})
            assert response.status_code == 400
    generic = pd.read_csv(ROOT/'tests/fixtures/spec_example.csv')
    generic['laser_power_w'] = 1000
    generic['travel_speed_mm_s'] = 8
    generic['shielding_gas_flow_l_min'] = 20
    response = client.post('/analyze',data={'process_type':'laser_ded','lsl':980},files={'file':('shared.csv',generic.to_csv(index=False).encode(),'text/csv')})
    assert response.status_code == 200
    assert len(response.json()['parameters']['columns']) == 3


def test_laser_ded_spread_signal_is_counted_separately_and_guides_investigation():
    result = client.get('/analyze',params={'process_type':'laser_ded','dataset':'laser_ded_unstable_shift','lsl':895}).json()
    p = result['signal_pareto']
    assert p['total_signals'] == 16 and p['flagged_builds'] == 15
    assert [r['cumulative_percent'] for r in p['categories']] == [62.5, 93.75, 100]
    spread = next(a for a in result['investigation_actions'] if a['id']=='spread_high')
    assert spread['build_ids'] == ['D024']
