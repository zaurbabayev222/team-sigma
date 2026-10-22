"""Validate seeded EB-PBF and laser DED fixtures, with independent stdlib arithmetic."""
import math
from pathlib import Path
from statistics import mean, stdev
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from app.profiles import PROFILES
from app.qc import analyze
from app.signals import signal_pareto
from data.generate_additional import datasets, CONFIG

# Frozen outputs, additionally checked below using independent sample-SD math.
EXPECTED = {
    'ebpbf_stable_capable': ('capable', 2.542352990922, 2.267524651003, 0, (0, 0, 0)),
    'ebpbf_stable_incapable': ('not capable', .402748228202, .359211147648, 16, (0, 0, 0)),
    'ebpbf_unstable_shift': ('not assessable', 1.757831244591, .535751041026, 4, (11, 13, 0)),
    'laser_ded_stable_capable': ('capable', 1.394479510245, 1.423374442989, 0, (0, 0, 0)),
    'laser_ded_stable_incapable': ('not capable', .231754374130, .236556543689, 22, (0, 0, 0)),
    'laser_ded_unstable_shift': ('not assessable', .863483584124, .444494069549, 12, (10, 5, 1)),
}


def validate():
    frames = {}
    for name, text in datasets().items():
        path = ROOT / 'data' / name
        assert path.read_bytes() == text.encode('utf-8'), name + ': reproduction differs'
        df = pd.read_csv(path)
        process = df.process_type.iloc[0]
        fields = ['process_type', 'build_id', 'build_date', 'uts_mpa'] + [p['column'] for p in PROFILES[process]['parameters']]
        assert list(df.columns) == fields and len(df) == 90
        assert df.process_type.eq(process).all() and not df.isna().any().any()
        groups = list(df.groupby('build_id', sort=False))
        assert len(groups) == 30 and all(len(g) == 3 for _, g in groups)
        assert df.build_date.is_monotonic_increasing
        pd.to_datetime(df.build_date, format='%Y-%m-%d', errors='raise')
        for col in fields[3:]:
            assert df[col].map(math.isfinite).all()
        for _, g in groups:
            assert g.build_date.nunique() == 1
            assert all(g[col].nunique() == 1 for col in fields[4:])
        result = analyze(df, 895, 'build_id', 'build_date', 'uts_mpa')
        verdict, cpk, ppk, failures, expected_counts = EXPECTED[path.stem]
        assert result['verdict'] == verdict and result['n_failures'] == failures
        assert math.isclose(result['cpk'], cpk, abs_tol=1e-10)
        assert math.isclose(result['ppk'], ppk, abs_tol=1e-10)
        # Independent n=3 arithmetic, no qc constants or estimators called here.
        average = mean(mean(g.uts_mpa) for _, g in groups)
        sbar = mean(stdev(g.uts_mpa) for _, g in groups)
        c4 = math.sqrt(math.pi) / 2
        sigma = sbar / c4
        total = stdev(df.uts_mpa)
        xlo, xhi = average - 3*sigma/math.sqrt(3), average + 3*sigma/math.sqrt(3)
        shi = (1 + 3*math.sqrt(1-c4*c4)/c4) * sbar
        assert math.isclose(result['sigma_short'], sigma, abs_tol=1e-10)
        assert math.isclose(result['sigma_total'], total, abs_tol=1e-10)
        assert math.isclose(result['xbar']['lcl'], xlo, abs_tol=1e-10)
        assert math.isclose(result['s_chart']['ucl'], shi, abs_tol=1e-10)
        assert math.isclose(cpk, (average - 895)/(3*sigma), abs_tol=1e-10)
        assert math.isclose(ppk, (average - 895)/(3*total), abs_tol=1e-10)
        assert failures == sum(v < 895 for v in df.uts_mpa)
        counts = (sum(mean(g.uts_mpa) < xlo for _, g in groups),
                  sum(mean(g.uts_mpa) > xhi for _, g in groups),
                  sum(stdev(g.uts_mpa) > shi for _, g in groups))
        assert counts == expected_counts
        p = signal_pareto(result)
        assert sum(counts) == p['total_signals']
        if 'unstable' not in name:
            assert result['shapiro_p'] > .05
        if process == 'laser_ded' and 'unstable' in name:
            assert p['total_signals'] == 16 and p['flagged_builds'] == 15
            assert next(r for r in p['categories'] if r['category'] == 'spread_high')['build_ids'] == ['D024']
        frames[path.stem] = df
        print(f'PASS: {name}: Cpk={cpk:.6f}; Ppk={ppk:.6f}; failures={failures}/90; signals={sum(counts)}; {verdict}')
    for process, config in CONFIG.items():
        base = frames[process + '_stable_capable']
        incapable = frames[process + '_stable_incapable']
        unstable = frames[process + '_unstable_shift']
        before = base.build_id < config['prefix'] + '020'
        assert base[before].equals(unstable[before])
        assert (incapable.uts_mpa - base.uts_mpa + config['offset']).abs().lt(1e-9).all()
        delta = unstable.uts_mpa - base.uts_mpa
        expected = pd.Series([-config['shift'] if not b else 0 for b in before], index=base.index, dtype=float)
        if process == 'laser_ded':
            expected.loc[base.build_id.eq('D024')] += [-60, 0, 60]
        assert (delta - expected).abs().lt(1e-9).all()
        context = 'preheat_temperature_c' if process == 'ebpbf' else 'powder_feed_rate_g_min'
        assert (unstable.loc[~before, context] - base.loc[~before, context] + (80 if process == 'ebpbf' else 1)).abs().lt(1e-9).all()
    print('PASS: six new synthetic fixtures; byte reproduction, schema, independent arithmetic and planted signals')


if __name__ == '__main__':
    validate()
