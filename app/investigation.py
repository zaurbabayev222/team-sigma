"""Deterministic investigation guidance from observed QC evidence, not causality.

No new statistic, trained model, machine setpoint or release decision is produced.
The caller supplies the same settings and process metadata used for analysis.
"""
import math


def investigation_actions(result, profile, min_builds=25, cpk_target=1.33):
    actions = []

    def add(key, title, evidence, action, builds=None):
        actions.append({'id': key, 'priority': len(actions) + 1, 'title': title,
                        'evidence': evidence, 'action': action, 'build_ids': builds or []})

    if result['n_failures']:
        add('coupon_failures', 'Review below-specification coupon results',
            f"{result['n_failures']} of {result['n_coupons']} measured coupons are below the entered LSL.",
            'Trace the failing coupons to their tensile-test reports and build travelers. Verify units, specimen preparation and customer acceptance requirements with the responsible quality engineer.')
    pareto = result['signal_pareto']
    if pareto['flagged_builds']:
        add('unstable', 'Investigate chart signals before interpreting capability',
            f"{pareto['total_signals']} chart signals on {pareto['flagged_builds']} builds; capability conclusion is withheld.",
            'Review build chronology, test conditions, material lots, orientation and post-processing around the affected builds. The signal Pareto prioritizes review frequency, not cause or severity.')
        for row in pareto['categories']:
            checks = {
                'mean_low': 'Compare the affected build means with earlier and later builds. Check test records and process changes; a low chart mean is separate from a coupon failing the LSL.',
                'mean_high': 'Check whether test conditions, coupon population or process records changed. This is a statistical shift; there is no upper strength specification in this analysis.',
                'spread_high': 'Check individual coupons, sampling locations, specimen preparation, test repeatability and consistency within each build. A spread signal does not identify its physical cause.',
            }
            add(row['category'], 'Review ' + row['label'],
                f"{row['count']} signal occurrences ({row['percent']:.1f}% of all signals).",
                checks[row['category']], row['build_ids'])
        add('baseline', 'Review the control-limit baseline',
            'Current limits use the entire uploaded log, including signaled builds.',
            'After engineering investigation, collect or designate a justified stable qualification baseline before prospective monitoring. Full-log limits can also flag builds before a planted shift; do not simply delete points to obtain a passing result.')
    if result['cpk'] is None or result['ppk'] is None:
        add('no_variation', 'Verify measurement resolution and coupon records',
            'At least one variation estimate is zero; capability indices are undefined.',
            'Check for rounded or duplicated measurements, instrument resolution and copied rows. Collect valid repeated measurements; zero observed variation does not prove perfect capability.')
    if result['n_builds'] < min_builds:
        add('sample_size', 'Collect more comparable builds',
            f"{result['n_builds']} builds supplied; configured minimum is {min_builds}.",
            'Add independent builds using the same defensible subgroup and test design. Extra coupons within an existing build do not replace independent builds.')
    if result['verdict'] == 'not capable':
        add('capability_gap', 'Plan a controlled capability-improvement study',
            f"No implemented chart signal; lower-side Cpk {result['cpk']:.3f} is below configured target {cpk_target}.",
            'Verify the customer LSL and measurement system, then use qualified engineering trials to study centering and within-build variation. Reassess stability and capability after changes; do not lower the customer requirement to obtain a pass.')
    elif result['verdict'] == 'capable':
        add('monitor', 'Continue monitoring under comparable conditions',
            f"Lower-side Cpk {result['cpk']:.3f} meets configured target {cpk_target}; no implemented chart signal.",
            'Retain process and test traceability and continue build-level monitoring. This statistical assessment does not qualify or release aerospace hardware.')
    if result.get('shapiro_p') is not None and result['shapiro_p'] < .05:
        add('normality', 'Review the strength distribution and test population',
            f"Pooled Shapiro-Wilk p = {result['shapiro_p']:.4g} is below diagnostic threshold 0.05; this does not change the backend verdict.",
            'Inspect the distribution and whether mixed conditions or a process shift explain it. Review suitability of normal-based indices with a statistician; a pooled diagnostic does not prove a within-build distribution or cause.')
    if pareto['flagged_builds'] or result['verdict'] == 'not capable':
        parameters = result.get('parameters', {})
        usable = []
        for p in profile['parameters']:
            column = p['column']
            values = [v for v in parameters.get('usual_range', {}).get(column, {}).values()]
            values += [b['values'].get(column) for b in parameters.get('flagged_builds', [])]
            if any(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
                usable.append(f"{p['label']} ({p['unit']})")
        if usable:
            add('process_records', 'Compare available ' + profile['label'] + ' records',
                'Usable recorded context: ' + ', '.join(usable) + '.',
                'Compare source records with build chronology and, where available, unflagged-build observed ranges. Those ranges are descriptive, not approved operating windows. Verify any proposed setting change through a qualified engineering study.')
        else:
            add('missing_context', 'Collect process context for investigation',
                'No usable optional process measurements are available for this comparison.',
                'Record relevant ' + profile['label'] + ' conditions: ' + ', '.join(p['label'] + ' (' + p['unit'] + ')' for p in profile['parameters']) + '. Keep material, orientation and post-processing traceability; do not infer causes from strength alone.')
    return actions
