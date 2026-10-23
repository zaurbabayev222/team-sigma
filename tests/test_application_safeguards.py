"""Regression tests for reproduced invalid-input and HTTP-500 failures."""
from io import StringIO
from pathlib import Path

from fastapi.testclient import TestClient
import pandas as pd
import pytest

from app.app import app
from app.qc import analyze

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app, raise_server_exceptions=False)


def upload(frame, process='lpbf', **settings):
    return client.post('/analyze',data={'lsl':'895','process_type':process,**settings},
                       files={'file':('records.csv',frame.to_csv(index=False).encode(),'text/csv')})


@pytest.mark.parametrize('column,value',[
    ('build_id',None),('build_id',''),('build_id','  '),
    ('build_date',None),('build_date',''),('build_date','  '),
])
def test_missing_group_identity_or_order_never_produces_a_verdict(column,value):
    frame = pd.read_csv(ROOT/'data/stable_capable.csv')
    frame.loc[:2,column] = value
    response = upload(frame)
    assert response.status_code == 400
    assert column in response.json()['detail']
    with pytest.raises(ValueError,match=column):
        analyze(frame,895,'build_id','build_date','uts_mpa')


@pytest.mark.parametrize('process',['lpbf','waam','ebpbf','laser_ded'])
def test_ambiguous_chronology_is_rejected_before_any_date_filter(process):
    frame = pd.read_csv(ROOT/'tests/fixtures/spec_example.csv')
    frame.loc[0,'build_date'] = '2099-01-01'
    response = upload(frame,process)
    assert response.status_code == 400
    assert 'conflicting' in response.json()['detail']


@pytest.mark.parametrize('value',['2026-02-30','10/01/2026','2026-1-1'])
def test_api_requires_unambiguous_valid_iso_calendar_dates(value):
    frame = pd.read_csv(ROOT/'data/stable_capable.csv')
    frame['build_date'] = value
    response = upload(frame)
    assert response.status_code == 400
    assert 'date' in response.json()['detail']


@pytest.mark.parametrize('settings',[{'min_builds':0},{'min_builds':1},{'cpk_target':-1},
                                      {'cpk_target':0},{'cpk_target':'inf'},{'cpk_target':'nan'}])
def test_invalid_decision_settings_are_rejected_on_get_and_upload(settings):
    response = client.get('/analyze',params={'dataset':'stable_incapable','lsl':895,**settings})
    assert response.status_code in (400,422)
    assert response.json()['detail']
    response = upload(pd.read_csv(ROOT/'data/stable_incapable.csv'),**settings)
    assert response.status_code in (400,422)
    assert response.json()['detail']


@pytest.mark.parametrize('process,column',[
    ('lpbf','chamber_oxygen_ppm'),('waam','arc_current_a'),
    ('ebpbf','beam_current_ma'),('laser_ded','powder_feed_rate_g_min'),
])
def test_infinite_optional_process_measurement_returns_actionable_400(process,column):
    frame = pd.read_csv(ROOT/'tests/fixtures/spec_example.csv')
    frame[column] = float('inf')
    response = upload(frame,process)
    assert response.status_code == 400
    assert column in response.json()['detail']


def test_large_equal_subgroups_do_not_overflow_chart_constant_calculation():
    frame = pd.DataFrame({'build_id':['A']*400+['B']*400,
                          'build_date':['2026-01-01']*400+['2026-01-02']*400,
                          'uts_mpa':list(range(900,1300))*2})
    response = upload(frame)
    assert response.status_code == 200
    assert response.json()['n_per_build'] == 400


def test_missing_specification_and_mixed_process_tags_are_rejected():
    source = (ROOT/'tests/fixtures/spec_example.csv').read_bytes()
    assert client.post('/analyze',files={'file':('test.csv',source,'text/csv')}).status_code == 422
    frame = pd.read_csv(StringIO(source.decode()))
    frame['process_type'] = ['lpbf','waam']*6
    assert upload(frame).status_code == 400
