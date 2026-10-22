"""Primary inspection categories, independent of strength or chart signals."""
import pandas as pd


def inspection_records(df, build_col='build_id', value_col='uts_mpa'):
    """Keep original 1-based data-row positions, even in a filtered view.

    Blank/missing is unrecorded; literal 'none' is an inspected coupon with no
    recorded defect. Labels describe one primary category, not all defects.
    """
    records = []
    present = 'primary_defect' in df.columns
    for position, (_, row) in enumerate(df.iterrows(), 1):
        value = row['primary_defect'] if present else None
        if pd.isna(value) or (isinstance(value, str) and not value.strip()):
            category, label = None, None
        else:
            if not isinstance(value, str) or len(value.strip()) > 80:
                raise ValueError(f'primary_defect must be text of at most 80 characters at data row {position}')
            label = value.strip()
            category = label.casefold()
        records.append({'row': position, 'build_id': str(row[build_col]),
                        'uts_mpa': float(row[value_col]), 'category': category, 'label': label})
    return records


def inspection_pareto(records, provided=True):
    """Count primary defective coupons; no-defect/unrecorded are not categories."""
    groups = {}
    inspected = no_defect = 0
    for record in records:
        category = record['category']
        if category is None:
            continue
        inspected += 1
        if category == 'none':
            no_defect += 1
            continue
        groups.setdefault(category, []).append(record)
    defective = inspected - no_defect
    cumulative, rows = 0, []
    for category in sorted(groups, key=lambda key: (-len(groups[key]), key)):
        entries = groups[category]
        count = len(entries)
        cumulative += count
        rows.append({'category': category, 'label': entries[0]['label'], 'count': count,
                     'percent': 100 * count / defective,
                     'cumulative_percent': 100 * cumulative / defective,
                     'build_ids': list(dict.fromkeys(r['build_id'] for r in entries)),
                     'coupon_rows': [r['row'] for r in entries]})
    return {'provided': provided, 'total_coupons': len(records),
            'inspected_coupons': inspected, 'unrecorded_coupons': len(records) - inspected,
            'no_defect_coupons': no_defect, 'defective_coupons': defective,
            'coverage_percent': 100 * inspected / len(records) if records else None,
            'denominator': 'coupons with a recorded primary defect', 'categories': rows}
