# Interactive Pareto investigation (H-14)

Select a process and **Inspection defect example**, enter the customer LSL and
select **Analyze builds**. Four separate synthetic inspection examples supplement
the original twelve strength scenarios. The active local review preview is
http://127.0.0.1:8001/dashboard/; the standard launch uses port 8000.

## Read and select categories

The signal Pareto counts existing chart-rule occurrences; the inspection Pareto
counts coupons with a recorded primary inspection defect. They have different
denominators. Both show count/share labels, cumulative percentages and a dashed
80% reference. That line does not prove an 80/20 relationship, severity or cause.

Click a bar, focus it and press Enter/Space, or use **Inspect** in the supporting
table. A selected bar has an outline and an announced pressed state. Selection:

- Narrows the build-investigation table to matching builds. Inspection categories
  can include unflagged builds; statistical signals and physical defects differ.
- Outlines those builds on the complete X-bar and S charts without changing flags.
- Shows scoped evidence-linked checks and recorded process context. Expand each
  build's coupon records for original data-row numbers, UTS and inspection labels.
- Retains each Pareto denominator; selecting one category does not make it 100%.

**Clear selection** restores flagged builds within the applied date view.
**Reset Pareto view** clears both the selection and the date bounds. The link
beside Clear selection takes the user to build details without an automatic jump.

## Date windows and unchanged assessment

**From build date** and **Through build date** are inclusive; either may be blank.
Select **Apply date range** to apply draft dates. The applied dates and build
count stay visible. Editing dates does not silently change the displayed view.
Use dates present in the file: the original LPBF examples and the other process
examples may cover different months.

Python always analyzes the full input first. Window counts use the original
full-log means, S values and control limits. Capability indices, verdict, failure
totals, diagnostics, original reference ranges and the complete strength charts
remain full-log results. This is descriptive filtering, not a new capability
analysis or a qualified prospective baseline. Scoped checks are explicitly labeled.

An empty window shows zero categories and an explanation, with no new capability
verdict. Reversed/invalid dates and conflicting/invalid source build dates produce
a recoverable error; the last successful view remains displayed. Source calendar
validation is required for date views, preserving legacy no-filter behavior.

## Inspection data contract

Optional CSV `primary_defect` has one primary classification per coupon:

| Value | Meaning | Included in defect bars? |
| --- | --- | --- |
| Recorded category, e.g. `Porosity` | Inspected; primary defect recorded | Yes |
| `none` (case-insensitive) | Inspected; no primary defect recorded | No |
| Blank or missing column | Inspection unrecorded/not supplied | No |

Trim labels and group case-insensitively. Ties use normalized alphabetic order.
Labels may contain up to 80 characters. Arbitrary recorded categories are supported;
the app does not infer them from strength or invent the inspection outcome. A
single primary category cannot inventory multiple defects on a coupon. Data-row
numbers are 1-based positions excluding the header and stay stable after filtering.

The dashboard reports inspected/total, coverage, defective, explicit no-defect and
unrecorded counts separately. Defect percentages and cumulative percentages use
only defective inspected coupons in the applied window. Absence of a column,
all results missing, all inspected/no-defect and an empty date window have distinct
messages. None establishes defect-free production or hardware acceptance.

## API and implementation

GET `/analyze` accepts optional query strings `start_date`, `end_date`,
`signal_category` (`mean_low`, `mean_high`, `spread_high`), `defect_category`
(a recorded label). POST accepts the same names as multipart fields. Select one
category kind at a time. Requests still send the complete dataset/file and LSL;
there is no server session, retained upload or database.

Responses retain all prior full-log fields and add `inspection_pareto` plus
`investigation_view`. The latter contains applied bounds, window/full build
counts, both scoped Paretos, selection, matching builds, build/coupon context,
scoped actions and the limits-source label. `inspection.py` and `pareto_view.py`
are plain Python functions. React performs presentation, geometry and requests;
all counting, percentages and date membership remain in Python. `qc.py` is unchanged.

## Verification examples

Recorded porosity 2, crack 1, none 1, blank 1 gives three defective, four inspected
and five total coupons; coverage 80%; percentages 66.6667/33.3333 and cumulative
66.6667/100. Missing/none labels and exact date edges have dedicated tests.

In Laser DED's inspection example, all dates give 39 primary defects across 84
inspected coupons (90 total). Porosity is 20/39, followed by lack of fusion 12/39,
cracking 5/39 and dimensional deviation 2/39. Filtering to 2026-10-24 retains
D024's low-mean and high-S signals: two occurrences on one build, each 50%,
with unchanged full-log Cpk/Ppk and withheld verdict. Selecting S shows one build;
clearing selection keeps the date range. See the [codebook](../data/README.md#synthetic-inspection-examples-h-14)
and [walkthrough](../demo/README.md#h-14-interactive-pareto-and-inspection-demo).
