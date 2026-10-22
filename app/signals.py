"""Descriptive Pareto of existing X-bar/S signals; never inspection defects.

Input is an already validated core analysis. Counts are rule occurrences, so a
build with a mean signal and an S signal contributes twice to the denominator.
"""

CATEGORIES = (
    ('mean_low', 'Mean below X-bar LCL'),
    ('mean_high', 'Mean above X-bar UCL'),
    ('spread_high', 'S above UCL'),
)


def signal_pareto(result):
    """Return descending signal counts, deterministic ties and cumulative %.

    Use the exact strict inequalities implemented by qc.analyze, rather than
    parsing prose reasons. Equality at a limit does not signal. Zero-count
    categories are omitted; no-signal input has an empty list, not 0/0.
    """
    ids = {key: [] for key, _ in CATEGORIES}
    for build in result['builds']:
        tests = (build['mean'] < result['xbar']['lcl'],
                 build['mean'] > result['xbar']['ucl'],
                 build['s'] > result['s_chart']['ucl'])
        for (key, _), matched in zip(CATEGORIES, tests):
            if matched:
                ids[key].append(build['build_id'])
    total = sum(map(len, ids.values()))
    ordered = sorted(CATEGORIES, key=lambda item: -len(ids[item[0]]))
    rows, cumulative = [], 0
    for key, label in ordered:
        count = len(ids[key])
        if not count:
            continue
        cumulative += count
        rows.append({'category': key, 'label': label, 'count': count,
                     'percent': 100 * count / total,
                     'cumulative_percent': 100 * cumulative / total,
                     'build_ids': ids[key]})
    return {'total_signals': total,
            'flagged_builds': len({bid for values in ids.values() for bid in values}),
            'denominator': 'signal occurrences', 'categories': rows}
