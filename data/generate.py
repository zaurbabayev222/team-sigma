"""Generate the three SPEC synthetic fixtures; no real measurements are used."""
import argparse
import csv
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
FIELDS = ['build_id', 'build_date', 'uts_mpa', 'chamber_oxygen_ppm',
          'powder_reuse_count', 'laser_power_w']


def datasets():
    strengths = random.Random(5300)
    process = random.Random(5301)
    baseline = [[round(strengths.gauss(950, 10), 3) for _ in range(3)] for _ in range(30)]
    parameters = [(round(process.gauss(40, 3), 3), i % 6,
                   round(process.gauss(200, 2), 3)) for i in range(30)]
    output = {}
    for name, offset in [('stable_capable.csv', 0), ('stable_incapable.csv', -45),
                         ('unstable_shift.csv', 0)]:
        stream = StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        for index, coupons in enumerate(baseline):
            shifted = name == 'unstable_shift.csv' and index >= 19
            oxygen, reuse, power = parameters[index]
            for strength in coupons:
                writer.writerow({
                    'build_id': f'B{index + 1:03}',
                    'build_date': (date(2026, 9, 1) + timedelta(days=index)).isoformat(),
                    'uts_mpa': f'{strength + offset - (35 if shifted else 0):.3f}',
                    'chamber_oxygen_ppm': f'{oxygen + (100 if shifted else 0):.3f}',
                    'powder_reuse_count': reuse,
                    'laser_power_w': f'{power:.3f}',
                })
        output[name] = stream.getvalue()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check byte reproducibility without rewriting')
    args = parser.parse_args()
    for name, contents in datasets().items():
        path = ROOT / name
        expected = contents.encode('utf-8')
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                parser.exit(1, f'FAIL: {name} differs from its seeded generator\n')
        else:
            path.write_bytes(expected)
        print(f'{"PASS" if args.check else "WROTE"}: {name}: 30 builds x 3 coupons (90 rows), synthetic')


if __name__ == '__main__':
    main()
