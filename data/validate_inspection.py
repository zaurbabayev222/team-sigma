"""Validate inspection fixtures without changing or inferring strength outcomes."""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from app.inspection import inspection_pareto, inspection_records
from app.qc import analyze
from data.generate_inspection import datasets, SOURCES


def validate():
    for name, text in datasets().items():
        path = ROOT / 'data' / name
        assert path.read_bytes() == text.encode('utf-8')
        process = name.removesuffix('_inspection_demo.csv')
        frame = pd.read_csv(path, converters={'primary_defect': str})
        source = pd.read_csv(ROOT / 'data' / SOURCES[process])
        pd.testing.assert_frame_equal(frame.drop(columns='primary_defect'), source)
        independent = Counter(frame.primary_defect.str.casefold())
        assert independent == Counter({'none':45,'':6,'porosity':20,'lack of fusion':12,'cracking':5,'dimensional deviation':2})
        p = inspection_pareto(inspection_records(frame))
        assert p['inspected_coupons'] == 84 and p['defective_coupons'] == 39
        assert p['coverage_percent'] == 100 * 84 / 90
        assert [r['count'] for r in p['categories']] == [20,12,5,2]
        assert [r['cumulative_percent'] for r in p['categories']] == [100*n/39 for n in [20,32,37,39]]
        assert sum(map(len,(r['coupon_rows'] for r in p['categories']))) == 39
        for df in [source,frame]:
            result = analyze(df,895,'build_id','build_date','uts_mpa')
            if df is source:
                expected = result
            else:
                assert result == expected
        print(f'PASS: {name}: 84/90 inspected; 39 primary defects; strength/core unchanged from source')
    print('PASS: four synthetic inspection examples, byte reproduction, independent counts and unchanged core outputs')


if __name__ == '__main__':
    validate()
