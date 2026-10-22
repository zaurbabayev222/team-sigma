"""Reproduce WAAM fixtures and cross-check their arithmetic independently of qc.py."""
import math
from pathlib import Path
from statistics import mean, stdev
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from app.qc import analyze
from data.generate_waam import FIELDS, datasets

COLUMNS = dict(subgroup_col='build_id', order_col='build_date', value_col='uts_mpa')
EXPECTED = {
    'waam_stable_capable.csv': ('capable', 1.911108251244, 1.891082633619, 0, []),
    'waam_stable_incapable.csv': ('not capable', .307909399777, .304682959883, 18, []),
    'waam_unstable_shift.csv': ('not assessable', 1.376708634089, .579596479790, 5,
                              [f'W{i:03}' for i in [3, 4, 5, 10, 14, 16, 17, *range(20, 31)]]),
}


def validate():
    frames = {}
    for name, text in datasets().items():
        path = ROOT / 'data' / name
        assert path.read_bytes() == text.encode('utf-8'), f'{name}: byte reproduction differs'
        df = pd.read_csv(path)
        frames[name] = df
        assert list(df.columns) == FIELDS and len(df) == 90
        assert not df.isna().any().any() and df.process_type.eq('waam').all()
        assert df.groupby('build_id').size().eq(3).all()
        assert df.groupby('build_id').build_date.nunique().eq(1).all()
        assert df.build_date.is_monotonic_increasing
        pd.to_datetime(df.build_date, format='%Y-%m-%d', errors='raise')
        for column in FIELDS[3:]:
            assert df[column].map(math.isfinite).all(), column
        for column in FIELDS[4:]:
            assert df.groupby('build_id')[column].nunique().eq(1).all(), column
        result = analyze(df, 895., **COLUMNS)
        verdict, cpk, ppk, failures, flags = EXPECTED[name]
        assert result['verdict'] == verdict
        if 'unstable' not in name:
            assert result['shapiro_p'] > .05, 'Stable synthetic reference should match normality assumption'
        assert math.isclose(result['cpk'], cpk, abs_tol=1e-10)
        assert math.isclose(result['ppk'], ppk, abs_tol=1e-10)
        assert result['n_failures'] == failures
        assert [b['build_id'] for b in result['builds'] if b['flagged']] == flags
        # Independent stdlib subgroup SDs and n=3 closed form: c4 = sqrt(pi)/2.
        sigma = mean(stdev(group.uts_mpa) for _, group in df.groupby("build_id")) / (math.sqrt(math.pi) / 2)
        average = mean(df.uts_mpa)
        assert math.isclose(result['sigma_short'], sigma, abs_tol=1e-10)
        assert math.isclose(result['sigma_total'], stdev(df.uts_mpa), abs_tol=1e-10)
        assert math.isclose(result['xbar']['center'], average, abs_tol=1e-10)
        assert math.isclose(result['xbar']['ucl'], average + 3 * sigma / math.sqrt(3), abs_tol=1e-10)
        assert math.isclose(result['cpk'], (average - 895) / (3 * sigma), abs_tol=1e-10)
        assert math.isclose(result['failure_rate'], failures / 90, abs_tol=1e-12)
        print(f'PASS: {name}: Cpk={cpk:.6f}; Ppk={ppk:.6f}; failures={failures}/90; flags={len(flags)}; {verdict}')
    baseline = frames['waam_stable_capable.csv']
    unstable = frames['waam_unstable_shift.csv']
    before = baseline.build_id < 'W020'
    assert baseline[before].equals(unstable[before])
    assert ((unstable.loc[~before, 'uts_mpa'] - baseline.loc[~before, 'uts_mpa']) + 50).abs().lt(1e-9).all()
    assert ((unstable.loc[~before, 'shielding_gas_flow_l_min'] - baseline.loc[~before, 'shielding_gas_flow_l_min']) + 5).abs().lt(1e-9).all()
    print('PASS: WAAM byte reproducibility, schema, independent arithmetic and planted W020 shift')


if __name__ == '__main__':
    validate()
