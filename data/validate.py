"""Check frozen synthetic scenarios, reproducibility and core edge behavior."""
from datetime import date
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from app.qc import analyze
from data.generate import FIELDS, datasets

LSL = 895
COLUMNS = {'subgroup_col': 'build_id', 'order_col': 'build_date', 'value_col': 'uts_mpa'}
EXPECTED = {
    'stable_capable.csv': ('capable', 1.683472027406637, 1.7888714257173952, 0, []),
    'stable_incapable.csv': ('not capable', 0.3119606023055329, 0.3314919394732296, 17, []),
    'unstable_shift.csv': ('not assessable', 1.2923372876555803, 0.7117306491588054, 0,
                          ['B007', 'B014', 'B018', 'B020', 'B024', 'B025',
                           'B026', 'B027', 'B028', 'B029', 'B030']),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_error(frame, expected):
    try:
        analyze(frame, LSL, **COLUMNS)
    except ValueError as exc:
        require(expected in str(exc), f'Unexpected error: {exc}')
    else:
        raise ValueError('Invalid data was accepted: ' + expected)


def main():
    try:
        frames = {}
        for name, contents in datasets().items():
            path = ROOT / 'data' / name
            require(path.read_bytes() == contents.encode(), f'{name}: seeded regeneration differs')
            frame = pd.read_csv(path)
            frames[name] = frame
            require(list(frame.columns) == FIELDS, f'{name}: schema differs')
            require(len(frame) == 90 and not frame.isna().any().any(), f'{name}: missing values/rows')
            require(frame.groupby('build_id').size().eq(3).all(), f'{name}: unequal coupons')
            require(frame.groupby('build_id')['build_date'].nunique().eq(1).all(), f'{name}: conflicting dates')
            require(frame['build_date'].is_monotonic_increasing, f'{name}: dates are not ordered')
            for value in frame['build_date']:
                require(date.fromisoformat(value).isoformat() == value, f'{name}: invalid date')
            for column in FIELDS[2:]:
                require(frame[column].map(math.isfinite).all(), f'{name}: nonfinite {column}')
            require((frame['powder_reuse_count'].ge(0) & frame['powder_reuse_count'].mod(1).eq(0)).all(), 'Invalid reuse count')
            for column in FIELDS[3:]:
                require(frame.groupby('build_id')[column].nunique().eq(1).all(), f'{name}: inconsistent build parameter')
            result = analyze(frame, LSL, **COLUMNS)
            verdict, cpk, ppk, failures, flags = EXPECTED[name]
            require(result['n_builds'] == 30 and result['n_per_build'] == 3, f'{name}: incorrect subgroup count')
            require(result['verdict'] == verdict, f'{name}: incorrect verdict')
            require(math.isclose(result['cpk'], cpk, abs_tol=1e-9), f'{name}: Cpk differs')
            require(math.isclose(result['ppk'], ppk, abs_tol=1e-9), f'{name}: Ppk differs')
            require(result['n_failures'] == failures, f'{name}: failure count differs')
            require(math.isclose(result['failure_rate'], failures / 90, abs_tol=1e-12), 'Failure fraction differs')
            require([b['build_id'] for b in result['builds'] if b['flagged']] == flags, f'{name}: flags differ')
            print(f'PASS: {name}: {verdict}; Cpk={result["cpk"]:.6f}; Ppk={result["ppk"]:.6f}; failures={failures}/90; flags={len(flags)}')

        stable = frames['stable_capable.csv']
        shifted = frames['unstable_shift.csv']
        before = stable['build_id'] < 'B020'
        require(shifted[before].equals(stable[before]), 'Shift starts before B020')
        require(((shifted.loc[~before, 'uts_mpa'] - stable.loc[~before, 'uts_mpa']) + 35).abs().lt(1e-9).all(), 'Strength shift is not -35 MPa')
        require(((shifted.loc[~before, 'chamber_oxygen_ppm'] - stable.loc[~before, 'chamber_oxygen_ppm']) - 100).abs().lt(1e-9).all(), 'Oxygen shift is not +100 ppm')
        require(((frames['stable_incapable.csv']['uts_mpa'] - stable['uts_mpa']) + 45).abs().lt(1e-9).all(), 'Incapable shift is not -45 MPa')
        print('PASS: shared baseline, incapable offset and planted B020 strength/oxygen shift')

        constant = stable.copy()
        constant['uts_mpa'] = 1000.0
        result = analyze(constant, LSL, **COLUMNS)
        require(result['cpk'] is None and result['ppk'] is None and result['verdict'] == 'not assessable' and 'no variation' in result['reason'], 'Constant data must not claim capability')
        check_error(stable.iloc[:3], 'need at least 2 builds')
        check_error(stable.drop(index=3), 'B002')
        missing = stable.copy()
        missing.loc[5, 'uts_mpa'] = float('nan')
        check_error(missing, 'row 5')
        print('PASS: constant data, one build, unequal coupons and missing strength')
        print('PASS: H-02 reproducibility, schema, scenario outcomes and edge cases')
    except (ValueError, OSError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
