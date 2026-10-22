"""Descriptive date/category views; never recalculate limits or capability."""
from copy import deepcopy
from datetime import date
import math
import re

import pandas as pd
if __package__:
    from .inspection import inspection_pareto
    from .signals import CATEGORIES, signal_pareto
else:  # flat Posit Connect entrypoint
    from inspection import inspection_pareto
    from signals import CATEGORIES, signal_pareto


def iso_date(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(label + ' must be an ISO date (YYYY-MM-DD)')
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(label + ' must be a valid calendar date') from None


def pareto_view(df, result, records, profile, start_date=None, end_date=None,
                signal_category=None, defect_category=None):
    """Category selection filters details only; date bounds define denominators.

    The full, validated core result and its control limits are read-only inputs.
    Source dates are checked only when date filtering is requested, preserving
    legacy no-filter handling while refusing ambiguous date-window membership.
    """
    labels = dict(CATEGORIES)
    if signal_category and signal_category not in labels:
        raise ValueError('unknown signal_category')
    if signal_category and defect_category:
        raise ValueError('select a signal_category or defect_category, not both')
    start = iso_date(start_date, 'start_date') if start_date else None
    end = iso_date(end_date, 'end_date') if end_date else None
    if start and end and start > end:
        raise ValueError('start_date must be on or before end_date')
    if start or end:
        for name, group in df.groupby(profile['subgroup_col'], sort=False):
            dates = group[profile['order_col']].astype(str)
            if dates.nunique() != 1:
                raise ValueError(f"build '{name}' has conflicting dates; correct the source before date filtering")
            iso_date(dates.iloc[0], f"build '{name}' date")
    window = [b for b in result['builds']
              if (not start or iso_date(b['order'], 'build date') >= start)
              and (not end or iso_date(b['order'], 'build date') <= end)]
    window_ids = {b['build_id'] for b in window}
    scoped_records = [r for r in records if r['build_id'] in window_ids]
    signal = signal_pareto({**result, 'builds': window})
    inspection = inspection_pareto(scoped_records, 'primary_defect' in df.columns)
    selection = None
    if signal_category:
        row = next((r for r in signal['categories'] if r['category'] == signal_category), None)
        chosen = set(row['build_ids']) if row else set()
        selection = {'kind': 'signal', 'category': signal_category, 'label': labels[signal_category]}
    elif defect_category:
        category = defect_category.strip().casefold()
        if not category or category == 'none' or len(category) > 80:
            raise ValueError('defect_category must name a primary defect, not none or blank')
        row = next((r for r in inspection['categories'] if r['category'] == category), None)
        chosen = set(row['build_ids']) if row else set()
        selection = {'kind': 'defect', 'category': category, 'label': row['label'] if row else defect_category.strip()}
    else:
        chosen = {b['build_id'] for b in window if b['flagged']}
    builds = [deepcopy(b) for b in window if b['build_id'] in chosen]
    context = []
    for build in builds:
        group = df[df[profile['subgroup_col']].astype(str).eq(build['build_id'])]
        values = {}
        for p in profile['parameters']:
            if p['column'] in group:
                numeric = pd.to_numeric(group[p['column']], errors='coerce')
                finite = numeric[numeric.map(lambda x: pd.notna(x) and math.isfinite(x))]
                values[p['column']] = float(finite.mean()) if len(finite) else None
        context.append({'build_id': build['build_id'], 'values': values,
                        'coupons': [r for r in scoped_records if r['build_id'] == build['build_id']]})
    filtered = bool(start or end or selection)
    actions = focused_actions(result, signal, inspection, selection, builds, profile) if filtered else deepcopy(result['investigation_actions'])
    if not filtered and inspection['defective_coupons']:
        actions.append(defect_action(inspection['categories'][0], len(actions) + 1))
    return {'start_date': start_date or None, 'end_date': end_date or None,
            'window_builds': len(window), 'full_builds': result['n_builds'],
            'signal_pareto': signal, 'inspection_pareto': inspection,
            'selection': selection, 'builds': builds, 'context': context,
            'actions': actions, 'filtered': filtered,
            'limits_source': 'full input log; unchanged',
            'window_build_ids': [b['build_id'] for b in window]}


def defect_action(row, priority):
    return {'id': 'inspection_review', 'priority': priority,
            'title': 'Review recorded inspection category: ' + row['label'],
            'evidence': f"{row['count']} coupons ({row['percent']:.1f}% of recorded primary defects in this date view).",
            'action': 'Trace these data rows to their original inspection reports, method, coverage and acceptance criteria. Confirm the primary classification with the responsible engineer. A recorded category is not a diagnosis of cause, a complete defect inventory or a printer-setting prescription.',
            'build_ids': row['build_ids']}


def focused_actions(result, signal, inspection, selection, builds, profile):
    """Produce scoped evidence while keeping global verdict/guidance separate."""
    actions = []
    source = {a['id']: a for a in result['investigation_actions']}
    for row in signal['categories']:
        if selection and (selection['kind'] != 'signal' or selection['category'] != row['category']):
            continue
        action = deepcopy(source[row['category']])
        action['evidence'] = f"{row['count']} signals ({row['percent']:.1f}% of signals in this date view); original full-log limits retained."
        action['build_ids'] = row['build_ids']
        actions.append(action)
    for row in inspection['categories']:
        if selection and (selection['kind'] != 'defect' or selection['category'] != row['category']):
            continue
        actions.append(defect_action(row, 0))
        if not selection:
            break  # most frequent recorded category; full table remains available
    if builds:
        actions.append({'id': 'view_records', 'priority': 0,
                        'title': 'Compare source records for the displayed builds',
                        'evidence': f"{len(builds)} displayed builds for {profile['label']}.",
                        'action': 'Review the coupon details and available recorded process context below. Unflagged-build reference ranges and the capability assessment still describe the full input log. Confirm comparable material, orientation, processing and test conditions before engineering trials.',
                        'build_ids': [b['build_id'] for b in builds]})
    if not actions:
        actions.append({'id': 'empty_view', 'priority': 0, 'title': 'No matching evidence in this view',
                        'evidence': 'No selected signal or recorded primary-defect category to investigate in the current view.',
                        'action': 'Clear the category selection or expand the date range. Absence of evidence in a filtered view does not change the full-log capability verdict or prove defect-free production.', 'build_ids': []})
    for i, action in enumerate(actions, 1):
        action['priority'] = i
    return actions
