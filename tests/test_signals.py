from copy import deepcopy

import pandas as pd
import pytest

from app.qc import analyze
from app.signals import signal_pareto


def test_known_answer_multiple_signals_ties_and_limit_equality():
    result = {'xbar': {'lcl': 90, 'ucl': 110}, 's_chart': {'ucl': 20},
              'builds': [dict(build_id=name, mean=mean, s=s) for name, mean, s in
                         [('A', 89, 21), ('B', 80, 10), ('C', 111, 10), ('D', 90, 20), ('E', 110, 20)]]}
    original = deepcopy(result)
    p = signal_pareto(result)
    assert p['total_signals'] == 4 and p['flagged_builds'] == 3
    assert [r['category'] for r in p['categories']] == ['mean_low', 'mean_high', 'spread_high']
    assert [r['count'] for r in p['categories']] == [2, 1, 1]
    assert [r['percent'] for r in p['categories']] == [50, 25, 25]
    assert [r['cumulative_percent'] for r in p['categories']] == [50, 75, 100]
    assert p['categories'][0]['build_ids'] == ['A', 'B']
    assert result == original


@pytest.mark.parametrize('builds', [[], [dict(build_id='A', mean=100, s=0)]])
def test_no_signals_has_no_percentage_or_phantom_defects(builds):
    p = signal_pareto({'builds': builds, 'xbar': {'lcl': 100, 'ucl': 100}, 's_chart': {'ucl': 0}})
    assert p['categories'] == [] and p['total_signals'] == p['flagged_builds'] == 0


def test_matches_core_flags_on_planted_shift_and_constant_data():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for name in ['unstable_shift', 'waam_unstable_shift']:
        frame = pd.read_csv(root / 'data' / (name + '.csv'))
        for constant in [False, True]:
            if constant:
                frame.uts_mpa = 1000
            result = analyze(frame, 895, 'build_id', 'build_date', 'uts_mpa')
            p = signal_pareto(result)
            assert p['flagged_builds'] == sum(b['flagged'] for b in result['builds'])
            if p['categories']:
                assert p['categories'][-1]['cumulative_percent'] == 100
