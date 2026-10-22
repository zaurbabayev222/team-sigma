from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.investigation import investigation_actions
from app.profiles.waam import PROFILE
from app.qc import analyze
from app.signals import signal_pareto

ROOT = Path(__file__).resolve().parents[1]


def evidence(name='waam_stable_capable', **settings):
    result = analyze(pd.read_csv(ROOT / 'data' / (name + '.csv')), 895,
                     'build_id', 'build_date', 'uts_mpa', **settings)
    result['signal_pareto'] = signal_pareto(result)
    return result


@pytest.mark.parametrize('scenario,expected,absent', [
    ('waam_stable_capable', {'monitor'}, {'unstable', 'capability_gap'}),
    ('waam_stable_incapable', {'coupon_failures', 'capability_gap', 'missing_context'}, {'monitor', 'unstable'}),
    ('waam_unstable_shift', {'coupon_failures', 'unstable', 'mean_low', 'mean_high', 'baseline', 'missing_context'}, {'monitor', 'capability_gap'}),
])
def test_scenario_guidance_is_evidence_linked_and_does_not_mutate(scenario, expected, absent):
    result = evidence(scenario)
    before = deepcopy(result)
    actions = investigation_actions(result, PROFILE)
    ids = {a['id'] for a in actions}
    assert expected <= ids and not absent & ids
    assert [a['priority'] for a in actions] == list(range(1, len(actions) + 1))
    assert result == before
    for a in actions:
        assert a['evidence'] and a['action']
        if a['id'] in {'mean_low', 'mean_high', 'spread_high'}:
            assert a['build_ids']


def test_custom_settings_and_zero_variation_are_not_passing_guidance():
    result = evidence(min_builds=40)
    actions = investigation_actions(result, PROFILE, min_builds=40)
    sample = next(a for a in actions if a['id'] == 'sample_size')
    assert '40' in sample['evidence'] and not any(a['id'] == 'monitor' for a in actions)
    result = evidence('waam_stable_incapable', cpk_target=.2)
    assert '0.2' in next(a['evidence'] for a in investigation_actions(result, PROFILE, cpk_target=.2) if a['id'] == 'monitor')
    df = pd.read_csv(ROOT / 'data/waam_stable_capable.csv').assign(uts_mpa=1000)
    result = analyze(df, 895, 'build_id', 'build_date', 'uts_mpa')
    result['signal_pareto'] = signal_pareto(result)
    assert [a['id'] for a in investigation_actions(result, PROFILE)] == ['no_variation']


def test_optional_context_and_normality_concerns_are_qualified():
    result = evidence('waam_unstable_shift')
    result['parameters'] = {'usual_range': {'arc_current_a': {'min': 120, 'max': 130}}}
    actions = investigation_actions(result, PROFILE)
    context = next(a for a in actions if a['id'] == 'process_records')
    assert 'Arc current (A)' in context['evidence']
    assert 'not approved operating windows' in context['action']
    assert any(a['id'] == 'normality' for a in actions)


def test_api_exposes_same_signal_counts_and_guidance_for_named_and_uploaded_data():
    client = TestClient(app)
    named = client.get('/analyze', params={'dataset':'waam_unstable_shift','process_type':'waam','lsl':895}).json()
    uploaded = client.post('/analyze', data={'process_type':'waam','lsl':'895'},
                           files={'file':('waam.csv',(ROOT/'data/waam_unstable_shift.csv').read_bytes(),'text/csv')}).json()
    assert named == uploaded
    assert named['signal_pareto']['total_signals'] == 18
    assert any(a['id'] == 'process_records' for a in named['investigation_actions'])
