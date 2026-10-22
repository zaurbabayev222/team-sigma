"""Six seeded synthetic EB-PBF/laser DED fixtures, not empirical strength models."""
import argparse
import csv
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from app.profiles import PROFILES, SCENARIOS

# Fixed seeds chosen before inspecting outputs. Settings independent of strength.
CONFIG = {
    'ebpbf': dict(seed=5304, mean=970, sd=14, prefix='E', offset=65, shift=65,
                  settings=[(12, 1), (60, 1), (1000, 50), (700, 15), (.02, .004)]),
    'laser_ded': dict(seed=5306, mean=960, sd=15, prefix='D', offset=55, shift=55,
                      settings=[(1000, 40), (6, .3), (8, .4), (20, 1), (12, .5)]),
}


def datasets():
    output = {}
    for process, config in CONFIG.items():
        strength_rng, context_rng = random.Random(config['seed']), random.Random(config['seed'] + 1)
        strengths = [[round(strength_rng.gauss(config['mean'], config['sd']), 3) for _ in range(3)] for _ in range(30)]
        settings = [[round(value + context_rng.uniform(-spread, spread), 4) for value, spread in config['settings']] for _ in range(30)]
        fields = ['process_type', 'build_id', 'build_date', 'uts_mpa'] + [p['column'] for p in PROFILES[process]['parameters']]
        for scenario in SCENARIOS:
            stream = StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            for i, coupons in enumerate(strengths):
                shifted = scenario == 'unstable_shift' and i >= 19
                values = settings[i].copy()
                if shifted:
                    values[3 if process == 'ebpbf' else 1] -= 80 if process == 'ebpbf' else 1
                for j, strength in enumerate(coupons):
                    uts = strength - (config['offset'] if scenario == 'stable_incapable' else 0)
                    if shifted:
                        uts -= config['shift']
                    if process == 'laser_ded' and scenario == 'unstable_shift' and i == 23:
                        uts += (-60, 0, 60)[j]  # deliberate spread increase, no causal model
                    row = [process, f"{config['prefix']}{i+1:03}", (date(2026, 10, 1) + timedelta(days=i)).isoformat(), f'{uts:.3f}']
                    writer.writerow(dict(zip(fields, row + [f'{value:.4f}' for value in values])))
            output[process + '_' + scenario + '.csv'] = stream.getvalue()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, text in datasets().items():
        path, expected = ROOT / name, text.encode('utf-8')
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                parser.exit(1, 'FAIL: seeded reproduction differs: ' + name + '\n')
        else:
            path.write_bytes(expected)
        print(('PASS' if args.check else 'WROTE') + ': ' + name + ': SYNTHETIC; 30 builds x 3 coupons')


if __name__ == '__main__':
    main()
