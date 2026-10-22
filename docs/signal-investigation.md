# Signal Pareto and investigation workflow

This describes the H-11 to H-13 foundation. [H-14](pareto-explorer.md) extends it with selection, fixed-limit date views and a separate primary-inspection-defect Pareto; the earlier inspection-category deferral below is historical.

Select LPBF, WAAM, EB-PBF or powder-fed laser DED, choose an example or upload
comparable coupon records, enter the customer LSL and select **Analyze builds**.
First read the assessment and observed failures, then the charts, signal Pareto,
recommended investigation actions and build investigation table.

## What the Pareto counts

The existing engine implements three strict chart rules: mean below X-bar LCL,
mean above X-bar UCL and within-build sample S above its UCL. Equality is not a
signal. `app/signals.py` counts those rule occurrences from core means, S values
and limits without parsing reason strings or changing the rules.

- A category is counted once per build. A build can contribute a mean and an S
  signal. Total occurrences can exceed unique flagged builds.
- Bars show counts, descending. Ties use low mean, high mean, high S order.
  Zero-count categories are omitted. The right-axis line shows cumulative percent.
- Percent = 100 x category count / total occurrences. Cumulative percent uses
  the running count with the same denominator. These are not defect rates,
  coupon failure rates, probabilities of causes or evidence of an 80/20 law.
- With no signals, show an empty-state explanation rather than fabricated bars
  or percentages. Inspection defect categories are deliberately deferred.
- Expand **Signal counts and affected builds** for exact values and build IDs.

Known-answer check: A has low mean + high S, B low mean, C high mean, D no signal.
Counts are 2, 1, 1, percentages 50, 25, 25 and cumulative 50, 75, 100. There are four
signals on three unique builds. Tests cover ties, equality, constant/empty input,
unchanged inputs and parity with the existing core flags.

## Recommended investigation actions

`app/investigation.py` produces deterministic checks with `id`, `priority`,
`title`, `evidence`, `action` and `build_ids`. Ordered checks cover:

1. Trace observed below-LSL coupons to test reports and customer requirements.
2. Investigate instability and its individual signal categories, then review
   whether a qualified stable baseline exists. Current limits use the full log.
3. Verify zero variation and insufficient independent build counts when present.
4. For stable incapability, plan qualified studies of centering and variation;
   for capability under configured checks, continue monitoring and traceability.
5. Review a pooled Shapiro-Wilk p below 0.05 as a diagnostic, without changing the
   verdict or asserting a cause. Inspect any mixed populations or shifts first.
6. Compare usable selected-profile records, or collect missing context. Observed
   unflagged-build ranges are descriptive, not approved operating windows.

The first three checks are visible; expand **More investigation checks** for the
rest and **Affected builds** for IDs. Priorities reflect review order, not FMEA
severity scores. The same API `min_builds` and `cpk_target` settings are used by
both the core and guidance. No ML, predicted strength, numerical setpoint changes,
causal diagnosis or hardware-release decision is generated.

## API additions and compatibility

Existing analysis fields, LPBF defaults and dataset IDs are retained. Responses
add `signal_pareto` and `investigation_actions`. The core `app/qc.py` is unchanged.
`GET /profiles` lists all four process IDs; `GET /datasets?process_type=laser_ded`
lists its three examples. Analysis GET uses a query `process_type`; POST uses
the multipart field. Generic CSVs rely on the declared process. Tagged mixed
processes and nonempty exclusive foreign-profile fields are rejected. Shared
names with identical units, such as laser power or gas flow, are allowed.

New IDs are `ebpbf` and `laser_ded`. Laser DED here specifically means powder-fed
laser DED, not all DED processes. Neither method changes the required columns,
equal rational-subgroup requirement, measured UTS units or customer-entered LSL.
The [codebook](../data/README.md#eb-pbf-and-powder-fed-laser-ded-h-13) defines all
new parameters, seeds, constructed shifts and expected outcomes.

## Verification and release

Run `python -m pytest tests`, the three dataset validators, frontend tests/build
and `python demo/check.py --base-url http://127.0.0.1:8001` for the active review
preview (use port 8000 for the documented standard launch). All twelve examples
must agree with the core. Review both native file uploads, mismatches, process
switching, stale results, zero signals and mobile/table keyboard access.

Regenerate and verify the Connect manifest only after runtime inputs and built
assets are final. Local verification does not establish public deployment.
The push-to-main workflow remains in place; this increment is held locally for
review before any commit, push or deployment.
