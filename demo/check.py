"""Capture actual demonstration results; never substitutes generated or fixture data."""
import argparse
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from app.qc import analyze

SCENARIOS = {
    'stable_capable.csv': 'capable',
    'stable_incapable.csv': 'not capable',
    'unstable_shift.csv': 'not assessable',
    'waam_stable_capable.csv': 'capable',
    'waam_stable_incapable.csv': 'not capable',
    'waam_unstable_shift.csv': 'not assessable',
}


def compare(expected, actual, path='result'):
    """Require API parity for every core field, including flags and chart limits."""
    if isinstance(expected, dict):
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f'{path}.{key} missing from API')
            compare(value, actual[key], f'{path}.{key}')
    elif isinstance(expected, list):
        assert len(expected) == len(actual), f'{path}: different lengths'
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, f'{path}[{index}]')
    elif isinstance(expected, float):
        assert isinstance(actual, (int, float)) and math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-10), f'{path}: {expected} != {actual}'
    else:
        assert expected == actual, f'{path}: {expected!r} != {actual!r}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Running local/deployed app URL; checks API parity too')
    parser.add_argument('--lsl', type=float, default=895)
    parser.add_argument('--output', type=Path, help='Write captured actual JSON only after all checks pass')
    args = parser.parse_args()
    missing = [name for name in SCENARIOS if not (ROOT / 'data' / name).is_file()]
    if missing:
        parser.exit(1, 'BLOCKED: H-02 datasets missing: ' + ', '.join(missing) + '. Restore the real team datasets before demonstrating H-05.\n')
    results = {}
    for name, verdict in SCENARIOS.items():
        frame = pd.read_csv(ROOT / 'data' / name)
        result = analyze(frame, args.lsl, subgroup_col='build_id', order_col='build_date', value_col='uts_mpa')
        assert result['n_builds'] == 30 and result['n_per_build'] == 3, f'{name}: expected 30 builds x 3 coupons'
        assert result['verdict'] == verdict, f'{name}: expected {verdict}, got {result["verdict"]}: {result["reason"]}'
        if name.endswith('unstable_shift.csv'):
            assert any(build['flagged'] for build in result['builds']), 'shift must flag builds'
            assert 'unstable' in result['reason'].lower(), 'shift must explain instability'
        else:
            assert not any(build['flagged'] for build in result['builds']), f'{name}: stable scenario has flags'
        if args.base_url:
            address = args.base_url.rstrip('/') + '/analyze?' + urlencode({'dataset': Path(name).stem, 'lsl': args.lsl, 'process_type': 'waam' if name.startswith('waam_') else 'lpbf'})
            with urlopen(address, timeout=30) as response:
                compare(result, json.load(response))
        results[name] = result
        print(f'{name}: Cpk={result["cpk"]:.6f}, Ppk={result["ppk"]:.6f}, failures={result["n_failures"]}/{result["n_coupons"]}, verdict={result["verdict"]}; ' + ('API parity PASS' if args.base_url else 'core PASS'))
    if args.output:
        args.output.write_text(json.dumps({'lsl': args.lsl, 'results': results}, indent=2, allow_nan=False) + '\n')
        print(f'Captured actual results: {args.output}')
    print('PASS: all six synthetic scenarios (LPBF + WAAM)' + (' and API parity.' if args.base_url else '. API/browser reproduction still required.'))


if __name__ == '__main__':
    main()
