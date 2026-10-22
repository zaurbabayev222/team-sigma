"""Profile adapters must preserve known arithmetic and prevent process mixing."""
from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.qc import analyze
from data.validate_waam import validate

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]
KNOWN = (ROOT / 'tests/fixtures/spec_example.csv').read_bytes()


def upload(contents, process_type='waam'):
    return client.post('/analyze', files={'file': ('spec.csv', contents, 'text/csv')},
                       data={'lsl': '980', 'process_type': process_type})


@pytest.mark.parametrize('process_type', ['lpbf', 'waam'])
def test_known_answer_and_degenerate_inputs_for_both_profiles(process_type):
    result = upload(KNOWN, process_type).json()
    assert result['profile']['name'] == process_type
    assert result['cpk'] == pytest.approx(.591, abs=.001)
    assert result['ppk'] == pytest.approx(.571, abs=.001)
    assert result['n_failures'] == 1 and result['verdict'] == 'not assessable'
    assert result['parameters']['columns'] == []
    frame = pd.read_csv(ROOT / 'tests/fixtures/spec_example.csv')
    frame['uts_mpa'] = 1000
    result = upload(frame.to_csv(index=False).encode(), process_type).json()
    assert result['cpk'] is None and result['ppk'] is None and 'no variation' in result['reason']
    for bad in [frame.iloc[:3], frame.drop(index=0), frame.assign(uts_mpa=float('nan'))]:
        assert upload(bad.to_csv(index=False).encode(), process_type).status_code == 400


def test_profile_metadata_and_filtered_catalog():
    profiles = client.get('/profiles').json()['profiles']
    assert [p['name'] for p in profiles] == ['lpbf', 'waam']
    assert len(profiles[1]['parameters']) == 5
    old = client.get('/datasets').json()['datasets']
    waam = client.get('/datasets?process_type=waam').json()['datasets']
    assert len(old) == len(waam) == 3
    assert all(not name.startswith('waam_') for name in old)
    assert all(name.startswith('waam_') for name in waam)
    assert client.get('/datasets?process_type=unknown').status_code == 422
    assert upload(KNOWN, 'unknown').status_code == 422


def test_cross_process_dataset_and_upload_rejection():
    assert client.get('/analyze?dataset=waam_stable_capable&lsl=895').status_code == 404
    assert client.get('/analyze?dataset=stable_capable&lsl=895&process_type=waam').status_code == 404
    lpbf = (ROOT / 'data/stable_capable.csv').read_bytes()
    assert upload(lpbf).status_code == 400
    frame = pd.read_csv(ROOT / 'data/waam_stable_capable.csv')
    assert upload(frame.to_csv(index=False).encode(), 'lpbf').status_code == 400
    frame.loc[0, 'process_type'] = 'lpbf'
    assert upload(frame.to_csv(index=False).encode()).status_code == 400
    frame['process_type'] = None
    assert upload(frame.to_csv(index=False).encode()).status_code == 400


def test_all_waam_scenarios_use_the_unchanged_core_and_process_units():
    for path in sorted((ROOT / 'data').glob('waam_*.csv')):
        frame = pd.read_csv(path)
        response = client.get('/analyze', params={'dataset':path.stem, 'lsl':895, 'process_type':'waam'})
        assert response.status_code == 200
        result = response.json()
        expected = analyze(frame,895.,subgroup_col='build_id',order_col='build_date',value_col='uts_mpa')
        assert {k:result[k] for k in expected} == expected
        assert result['profile']['name'] == 'waam'
        assert 'arc_current_a' in result['parameters']['columns']
        assert 'laser_power_w' not in result['parameters']['columns']
        assert sum(bin['count'] for bin in result['histogram']) == 90


def test_seeded_waam_scenarios_against_independent_arithmetic():
    validate()


def test_empty_foreign_placeholders_are_not_required_or_imputed():
    frame = pd.read_csv(ROOT / 'tests/fixtures/spec_example.csv')
    frame['laser_power_w'] = None
    response = upload(frame.to_csv(index=False).encode())
    assert response.status_code == 200
    assert response.json()['parameters']['columns'] == []
