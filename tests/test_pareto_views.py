from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.app import app, run_analysis
from app.inspection import inspection_records, inspection_pareto

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def frame(labels):
    return pd.DataFrame({'build_id': [f'B{i // 3 + 1}' for i in range(len(labels))],
                         'uts_mpa': [900 + i for i in range(len(labels))], 'primary_defect': labels})


def test_known_inspection_counts_coverage_casefold_and_missing_semantics():
    records = inspection_records(frame(['Porosity', ' porosity ', 'Crack', 'none', '']))
    p = inspection_pareto(records)
    assert [r['count'] for r in p['categories']] == [2, 1]
    assert [r['percent'] for r in p['categories']] == pytest.approx([200/3, 100/3])
    assert [r['cumulative_percent'] for r in p['categories']] == pytest.approx([200/3, 100])
    assert (p['total_coupons'],p['defective_coupons'],p['inspected_coupons'],p['no_defect_coupons'],p['unrecorded_coupons']) == (5,3,4,1,1)
    assert p['coverage_percent'] == 80
    assert p['categories'][0]['coupon_rows'] == [1,2]


@pytest.mark.parametrize('labels,inspected,no_defect', [([],0,0),(['none','NONE'],2,2),(['',None],0,0)])
def test_distinct_zero_states_have_no_phantom_categories(labels, inspected, no_defect):
    p = inspection_pareto(inspection_records(frame(labels)))
    assert not p['categories'] and p['defective_coupons'] == 0
    assert p['inspected_coupons'] == inspected and p['no_defect_coupons'] == no_defect
    assert p['coverage_percent'] is None if not labels else p['coverage_percent'] in (0,100)


def test_missing_column_ties_and_bad_labels():
    p = inspection_pareto(inspection_records(frame(['none','none']).drop(columns='primary_defect')), provided=False)
    assert not p['provided'] and p['unrecorded_coupons'] == 2
    p = inspection_pareto(inspection_records(frame(['Zeta','Alpha'])))
    assert [r['category'] for r in p['categories']] == ['alpha','zeta']
    for value in [42, 'x'*81]:
        with pytest.raises(ValueError, match='primary_defect'):
            inspection_records(frame([value]))


def analyze_view(**filters):
    df = pd.read_csv(ROOT/'data/laser_ded_unstable_shift.csv')
    return run_analysis(df,895,25,1.33,'laser_ded',**filters)


def test_single_build_window_uses_original_limits_not_new_analysis():
    original = analyze_view()
    filtered = analyze_view(start_date='2026-10-24',end_date='2026-10-24',signal_category='spread_high')
    for field in ['xbar','s_chart','cpk','ppk','verdict','n_failures','builds','signal_pareto','investigation_actions']:
        assert filtered[field] == original[field]
    v = filtered['investigation_view']
    assert v['window_builds'] == 1 and [b['build_id'] for b in v['builds']] == ['D024']
    assert v['signal_pareto']['total_signals'] == 2 and v['signal_pareto']['flagged_builds'] == 1
    assert [r['percent'] for r in v['signal_pareto']['categories']] == [50,50]
    assert v['context'][0]['values']['powder_feed_rate_g_min'] is not None
    assert len(v['context'][0]['coupons']) == 3
    assert [a['id'] for a in v['actions']] == ['spread_high','view_records']
    assert '2 signals' not in v['actions'][0]['evidence']  # selected category has one occurrence


def test_open_bounds_empty_windows_and_selection_do_not_change_denominator():
    original = analyze_view()
    selected = analyze_view(signal_category='spread_high')
    assert selected['investigation_view']['signal_pareto'] == original['signal_pareto']
    assert selected['investigation_view']['actions'][0]['build_ids'] == ['D024']
    assert analyze_view(start_date='2026-10-30')['investigation_view']['window_builds'] == 1
    assert analyze_view(end_date='2026-10-01')['investigation_view']['window_builds'] == 1
    empty = analyze_view(start_date='2027-01-01')['investigation_view']
    assert empty['window_builds'] == 0 and empty['signal_pareto']['total_signals'] == 0
    assert empty['inspection_pareto']['coverage_percent'] is None and empty['builds'] == []
    assert empty['actions'][0]['id'] == 'empty_view'


@pytest.mark.parametrize('filters', [
    {'start_date':'2026-02-30'},{'end_date':'10/24/2026'},
    {'start_date':'2026-10-25','end_date':'2026-10-24'},
    {'signal_category':'fake'},{'signal_category':'mean_low','defect_category':'porosity'},
    {'defect_category':'none'},
])
def test_bad_filters_return_recoverable_errors(filters):
    response = client.get('/analyze',params={'dataset':'laser_ded_unstable_shift','process_type':'laser_ded','lsl':895,**filters})
    assert response.status_code == 400 and response.json()['detail']


def test_source_date_ambiguity_is_rejected_only_when_requesting_date_window():
    df = pd.read_csv(ROOT/'tests/fixtures/spec_example.csv')
    df.loc[0,'build_date'] = 'bad-date'
    assert run_analysis(df,980,25,1.33)['n_builds'] == 4
    with pytest.raises(HTTPException, match='conflicting dates'):
        run_analysis(df,980,25,1.33,start_date='2026-01-01')
    df.loc[:2,'build_date'] = '2026-02-30'
    with pytest.raises(HTTPException, match='valid calendar date'):
        run_analysis(df,980,25,1.33,end_date='2026-10-01')


def test_inspection_selection_includes_unflagged_builds_and_uses_coupon_denominator():
    df = pd.read_csv(ROOT/'data/waam_stable_capable.csv')
    df['primary_defect'] = 'none'
    df.loc[:1,'primary_defect'] = 'Porosity'
    df.loc[3,'primary_defect'] = 'Crack'
    before = deepcopy(df)
    result = run_analysis(df,895,25,1.33,'waam',defect_category='porosity')
    v = result['investigation_view']
    assert result['verdict'] == 'capable' and not result['signal_pareto']['categories']
    assert [b['build_id'] for b in v['builds']] == ['W001'] and not v['builds'][0]['flagged']
    assert v['inspection_pareto']['defective_coupons'] == 3
    assert v['actions'][0]['id'] == 'inspection_review' and '66.7%' in v['actions'][0]['evidence']
    assert 'porosity' in v['selection']['category']
    pd.testing.assert_frame_equal(df,before)


def test_upload_get_filter_parity_and_literal_none_survives_csv_parser():
    path = ROOT/'data/laser_ded_unstable_shift.csv'
    fields = {'process_type':'laser_ded','lsl':'895','start_date':'2026-10-24','end_date':'2026-10-24','signal_category':'spread_high'}
    named = client.get('/analyze',params={'dataset':path.stem,**fields}).json()
    uploaded = client.post('/analyze',data=fields,files={'file':(path.name,path.read_bytes(),'text/csv')}).json()
    assert named == uploaded
    df = pd.read_csv(path); df['primary_defect'] = 'None'
    response = client.post('/analyze',data={'process_type':'laser_ded','lsl':'895'},files={'file':('none.csv',df.to_csv(index=False).encode(),'text/csv')})
    assert response.status_code == 200
    assert response.json()['inspection_pareto']['no_defect_coupons'] == 90


def test_inspection_fixture_generation_and_independent_counts():
    from data.validate_inspection import validate
    validate()


@pytest.mark.parametrize('process', ['lpbf','waam','ebpbf','laser_ded'])
def test_inspection_demo_filtered_named_upload_parity_and_unknown_category(process):
    name=process+'_inspection_demo'
    path=ROOT/'data'/(name+'.csv')
    dates=pd.read_csv(path).build_date.drop_duplicates().tolist()
    fields={'lsl':'895','process_type':process,'start_date':dates[19],'end_date':dates[24],'defect_category':'porosity'}
    named=client.get('/analyze',params={'dataset':name,**fields})
    uploaded=client.post('/analyze',data=fields,files={'file':(path.name,path.read_bytes(),'text/csv')})
    assert named.status_code == uploaded.status_code == 200
    assert named.json() == uploaded.json()
    full=named.json()['inspection_pareto']
    scoped=named.json()['investigation_view']['inspection_pareto']
    assert full['defective_coupons'] == 39 and scoped['total_coupons'] == 18
    unknown=client.get('/analyze',params={'dataset':name,'lsl':895,'process_type':process,'defect_category':'unknown label'}).json()['investigation_view']
    assert unknown['builds'] == [] and unknown['actions'][0]['id'] == 'empty_view'
