"""Seeded stylized WAAM fixtures. No empirical physics or model training."""
import argparse
import csv
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
FIELDS = ['process_type', 'build_id', 'build_date', 'uts_mpa', 'arc_current_a',
          'arc_voltage_v', 'wire_feed_rate_m_min', 'travel_speed_mm_s',
          'shielding_gas_flow_l_min']


def datasets():
    strengths_rng, settings_rng = random.Random(5302), random.Random(5303)
    strengths = [[round(strengths_rng.gauss(960, 12), 3) for _ in range(3)]
                 for _ in range(30)]
    settings = [tuple(round(value + settings_rng.uniform(-spread, spread), 3)
                      for value, spread in [(125, 4), (12, .4), (1.5, .08), (4, .2), (18, .8)])
                for _ in range(30)]
    output = {}
    for scenario, offset in [('stable_capable', 0), ('stable_incapable', -55), ('unstable_shift', 0)]:
        stream = StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        for i, coupons in enumerate(strengths):
            shift = scenario == 'unstable_shift' and i >= 19
            for strength in coupons:
                current, voltage, feed, travel, gas = settings[i]
                writer.writerow(dict(zip(FIELDS, [
                    'waam', f'W{i + 1:03}', (date(2026, 10, 1) + timedelta(days=i)).isoformat(),
                    f'{strength + offset - (50 if shift else 0):.3f}',
                    current, voltage, feed, travel, f'{gas - (5 if shift else 0):.3f}',
                ])))
        output['waam_' + scenario + '.csv'] = stream.getvalue()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, text in datasets().items():
        path, expected = ROOT / name, text.encode('utf-8')
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                parser.exit(1, f'FAIL: {name} differs from seeded generation\n')
        else:
            path.write_bytes(expected)
        print(f'{"PASS" if args.check else "WROTE"}: {name}: 30 builds x 3 coupons, SYNTHETIC WAAM')


if __name__ == '__main__':
    main()
