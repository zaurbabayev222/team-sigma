"""Four separate synthetic inspection examples; original strength CSVs unchanged."""
import argparse
import csv
from io import StringIO
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
SOURCES = {process: ('' if process == 'lpbf' else process + '_') + 'unstable_shift.csv'
           for process in ['lpbf', 'waam', 'ebpbf', 'laser_ded']}


def datasets():
    output = {}
    for i, (process, source) in enumerate(SOURCES.items()):
        with (ROOT / source).open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            rows, fields = list(reader), reader.fieldnames
        labels = ['none']*45 + ['']*6 + ['Porosity']*20 + ['Lack of fusion']*12 + ['Cracking']*5 + ['Dimensional deviation']*2
        assert len(rows) == len(labels) == 90
        random.Random(5310 + i).shuffle(labels)
        stream = StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=fields + ['primary_defect'], lineterminator='\n')
        writer.writeheader()
        for row, label in zip(rows, labels):
            writer.writerow({**row, 'primary_defect': label})
        output[process + '_inspection_demo.csv'] = stream.getvalue()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, text in datasets().items():
        path, expected = ROOT / name, text.encode('utf-8')
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                parser.exit(1, 'FAIL: synthetic inspection reproduction differs: ' + name + '\n')
        else:
            path.write_bytes(expected)
        print(('PASS' if args.check else 'WROTE') + ': ' + name + ': SYNTHETIC INSPECTION; 39 primary defects, 45 none, 6 unrecorded')


if __name__ == '__main__':
    main()
