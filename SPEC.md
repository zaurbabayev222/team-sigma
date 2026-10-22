# SPEC: Six Sigma Hackathon team project

What your tool IS. Your agent reads this before every task. Where the code and this file
disagree, the code is the bug: change this file first, then the code.

Most of this page is already decided by the event and the [rubric](docs/criteria.md).
**Only the `FILL IN` lines change, and you do not have to write them by hand:** describe your app and ask your agent to update them. They depend on the prompt your team picks at kickoff
(prompts are secret until then, see [`docs/prompts.md`](docs/prompts.md)) and on your team.
The examples after each `FILL IN` show the shape of an answer. They are not hints about the prompts.

## 1. Team and prompt
- **Team name:** Sigma Airlines
- **Track:** Virtual DL Challenge (7 days). See [`docs/schedule.md`](docs/schedule.md).
- **Prompt we chose:** Prompt 1, "Industrial Systems, 3D Printing for Aerospace", from the [Devpost](https://six-sigma-hackathon.devpost.com/) challenge page:
  > An aerospace contractor 3D-printing titanium brackets is failing client strength tests. They don't
  > currently track enough environmental and stress parameters against final part strength. Design a
  > tool to monitor and flag when and whether the printing process is capable of meeting strict
  > aerospace tolerances, and help contractors resolve these issues.
- **Our public repo:** github.com/zaurbabayev222/team-sigma

## 2. User and use case (rubric: scope 5, user and use case 5)
- **User:** the contractor's quality engineer who reviews tensile-test results for each finished
  titanium build using LPBF, WAAM, EB-PBF or powder-fed laser DED.
- **Decision the tool helps them make, and when:** after each new build is tested, (1) whether the
  printing process has changed and needs investigating before the next build, and (2) whether the
  process is capable of meeting the customer's minimum strength, and if not, which recorded process
  parameter to look at first.
- **Why this matches the prompt:** it monitors and flags *when* the process goes out of control and
  *whether* it is capable of meeting the customer's strength requirement, and points to the
  parameters that moved, to help the contractor resolve failing strength tests.

## 3. Inputs (rubric: minimal inputs 5)
Only what this user can actually measure or already knows. Fewer is better; every input a user
cannot measure costs points.

| Input | Type and units | Where the user gets it |
|---|---|---|
| Printing process (required) | `lpbf`, `waam`, `ebpbf` or `laser_ded` | manufacturing record; selected in dashboard or API |
| `process_type` (optional CSV column) | consistent selected process ID | manufacturing record |
| `builds.csv`, one row per tested coupon | CSV file | their tensile-test log |
| `build_id` (required) | text | build traveler / printer job name |
| `build_date` (required) | date, YYYY-MM-DD; sets the build order | printer job log |
| `uts_mpa` (required) | numeric, MPa (ultimate tensile strength) | tensile-test report |
| Customer minimum strength, LSL (required) | numeric, MPa; typed in, not in the CSV | customer specification |
| `chamber_oxygen_ppm` (optional) | numeric, ppm | printer log |
| `powder_reuse_count` (optional) | integer, times the powder was reused | powder lot record |
| `laser_power_w` (LPBF optional) | numeric, W | printer job settings |
| `arc_current_a` (WAAM optional) | numeric, A | welding power-source log |
| `arc_voltage_v` (WAAM optional) | numeric, V | welding power-source log |
| `wire_feed_rate_m_min` (WAAM optional) | numeric, m/min | wire feeder log |
| `travel_speed_mm_s` (WAAM optional) | numeric, mm/s | motion controller log |
| `shielding_gas_flow_l_min` (WAAM optional) | numeric, L/min | gas flow record |

Every build has the same number of coupons (3 in our datasets). A blank `uts_mpa` is an error that
names the row, never a pass. The optional columns come from the selected *process profile*
(the four registered modules under `app/profiles/`); the statistics never read them.

## 4. The statistics, and why (rubric: valid QC analysis 25)
Say the method in words before any code exists. Load the `stats-first-steering` skill first.
- **Method:** an X-bar and S chart of tensile strength, one subgroup per build (its n coupons, n
  fixed per file), limits from the average within-build standard deviation; lower-side capability
  Cpk and performance Ppk against the customer minimum (LSL); and the coupon failure rate.
  - Center line X̿ = mean of the build means; s̄ = mean of the build standard deviations (n − 1).
  - X-bar limits: X̿ ± A3·s̄. S limits: B3·s̄ to B4·s̄. For n = 3: c4 = 0.8862, A3 = 1.954,
    B3 = 0, B4 = 2.568 (computed from n in code, not typed in).
  - σ_short = s̄ / c4. σ_total = standard deviation of all coupons (n − 1).
  - Cpk (lower) = (X̿ − LSL) / (3·σ_short). Ppk (lower) = (X̿ − LSL) / (3·σ_total).
  - Failure rate = coupons with uts_mpa < LSL ÷ all coupons.
  - A build is flagged out of control if its mean is outside the X-bar limits or its s is above B4·s̄.
  - Verdict: "not assessable" if any build is flagged or there are fewer than 25 builds (the numbers
    are still shown, with the reason); else "capable" if Cpk ≥ 1.33; else "not capable". The 1.33
    threshold is a setting, not hard-coded.
- **Why it fits the use case:** builds are natural subgroups (coupons printed together share one
  run), so the X-bar chart flags a build that shifted, the S chart flags uneven builds, and capability
  is measured on individual coupons, the level the customer tests at.
- **Assumptions and how the tool checks them:** coupon strengths are roughly normal within a stable
  process (histogram plus Shapiro-Wilk p-value shown); builds are in time order (sorted by
  `build_date`); equal coupons per build (checked, clear error if not); the strength spec has a
  minimum only, so there is no upper limit and no two-sided Cp/Pp.
- **Known-answer check:** 4 builds × 3 coupons, LSL = 980 MPa (illustrative arithmetic only, not a
  real titanium limit):

  | build | coupons (MPa) | mean | s |
  |---|---|---|---|
  | B1 | 990, 1000, 1010 | 1000 | 10 |
  | B2 | 1005, 1010, 1015 | 1010 | 5 |
  | B3 | 975, 990, 1005 | 990 | 15 |
  | B4 | 990, 1000, 1010 | 1000 | 10 |

  X̿ = 1000; s̄ = 10; X-bar limits 980.46 to 1019.54; S limits 0 to 25.68; no build flagged;
  σ_short = 11.284; σ_total = 11.677; Cpk (lower) = 0.591; Ppk (lower) = 0.571;
  failure rate = 1/12 = 8.3% (the 975 coupon); verdict "not assessable: fewer than 25 builds".
  Degenerate cases: all coupons equal → σ = 0, so Cpk and Ppk are None with the message "no
  variation"; one build → error "need at least 2 builds"; unequal coupons per build or a blank
  `uts_mpa` → an error naming the build or row.

Fixed for every team:
- The statistic lives in **one plain, tested function** (`app/qc.py` or `app/qc.R`). The API, app or
  package only calls it and displays the result. No statistics inside UI code.
- Every statistic has a test against a known answer and a degenerate case (constant data, n = 1, missing values).
- You can explain every number the tool prints. If you cannot, it is not done.

## 5. Delivery (rubric: working tool 25)
- **Stack:** REST API (FastAPI, Python) with a React (Vite, plain JavaScript) dashboard. Python
  computes every number; React only displays them.
- **Starting demo:** `demos/fastapi/` copied into `app/`, with `demos/reactfront/` as `app/frontend/`.
- **Built to expand:** the statistics in `app/qc.py` see only generic columns (subgroup id, order,
  value, lower limit). Process-specific fields live in the four registered modules under `app/profiles/`
  (its optional parameters, units and labels). Adding EB-PBF or other DED variants later means adding and registering a profile
  file, not changing the statistics. See [`docs/decisions.md`](docs/decisions.md).

Fixed for every team:
- Start from **one** demo in `demos/`, copied to `app/`. Keep its four-script contract
  (`testme`, `manifestme`, `deployme`, `README.md`); `testme` starts the tool with one command.
- Deployed on the course **Posit Connect** server with a public URL (publisher key handed out at the
  event). Deploy early: copy one workflow from
  [`.claude/skills/connect-publish/workflows/`](.claude/skills/connect-publish/workflows/).
- A small tool that runs beats a large tool that does not.

## 6. Outputs
- **What the user sees:** an X-bar chart and an S chart of tensile strength (MPa) by build, with
  out-of-control builds in red; Cpk and Ppk (lower) with the failure rate; and a verdict, "capable",
  "not capable" or "not assessable", with its reason. How to read this: red builds mean something
  changed in that build, so look at its process parameters; "capable" means the process reliably
  stays above the customer minimum. When optional parameters are present, a small table shows each
  parameter's value for the flagged builds next to its usual range.

## 7. Test datasets and codebook (rubric: demo 10, datasets 5, codebook 5)
The original three LPBF CSVs in `data/` remain the core rubric demonstration; H-10 adds three supplementary synthetic WAAM CSVs, one per scenario. Each file demonstrates one behavior.
`data/README.md` is the codebook: every file, every column with units, and what it would take to
collect this data for real.
- **Datasets:** 30 builds × 3 coupons each, fixed random seeds, all clearly labeled synthetic:
  `stable_capable.csv` (in control, Cpk ≥ 1.33), `stable_incapable.csv` (in control, mean too close
  to the LSL, Cpk < 1.33), `unstable_shift.csv` (chamber oxygen rises from build 20 on and strength
  drops, so builds are flagged and the verdict is "not assessable").

## 8. Documentation and reproducibility (rubric: docs 10, public repo 5)
- `README.md` says what the tool does, for whom, every input and parameter, how to run it in one
  command, and walks through the demo on each test dataset.
- Public GitHub repo; a fresh clone runs `testme` and the tests pass with no extra steps.
- Submit on Devpost: the repo link plus a demo.

## 9. Out of scope
What we will NOT build, so nobody (human or agent) builds it by accident.
- Default: logins, databases, real customer data, a second statistic before the first one is tested.
- Processes other than LPBF, WAAM, EB-PBF and powder-fed laser DED remain out of scope. Inspection primary-defect categories are supported by H-14.
- Regression, ANOVA, FMEA, machine learning or forecasting; two-sided Cpk on dimensions; filters by
  machine or lot; files with unequal coupons per build. Later, only after the core passes review.
- Certifying parts: the tool supports a decision, it does not release hardware.

## 10. Approved WAAM increment (H-10)

The user approved process selection, a WAAM profile, three synthetic WAAM scenarios and verification while retaining the LPBF baseline. All formulas, verdict rules and the section 4 known-answer and degenerate checks remain unchanged. The analysis assesses measured tensile strength; it does not predict strength from manufacturing settings.

- Select `process_type=lpbf` or `waam`. Existing clients that omit it retain LPBF behavior. A dataset from one process cannot be analyzed under the other process selection.
- Required columns remain `build_id`, `build_date`, `uts_mpa`; LSL is entered separately. Optional CSV `process_type`, when supplied, must consistently match the selection. Mixed processes are rejected rather than pooled. Nonempty recognized fields exclusive to another profile are rejected to prevent accidental mislabeling; a generic three-column file relies on the user's declared process.
- WAAM optional columns: `arc_current_a` (A), `arc_voltage_v` (V), `wire_feed_rate_m_min` (m/min), `travel_speed_mm_s` (mm/s), `shielding_gas_flow_l_min` (L/min). LPBF fields are not required for WAAM.
- Treat each build as one rational subgroup with the same number of comparable coupons. Do not mix alloys, test orientations, heat-treatment conditions or testing methods in one assessment. A process name alone does not justify this sampling design.
- Retain the three original LPBF CSVs and add `waam_stable_capable.csv`, `waam_stable_incapable.csv`, `waam_unstable_shift.csv`, each 30 builds x 3 coupons. The expanded demonstration has three scenarios per process; it does not replace the rubric's original three LPBF examples.
- WAAM data are seeded synthetic normal-reference fixtures, not measurements or a trained manufacturing model. All example strengths, parameters and LSL 895 MPa are illustrative. No operating window, causal effect or aerospace threshold is asserted.
- Known answer for both profile adapters: the section 4 CSV at LSL 980 must reproduce Cpk 0.591, Ppk 0.571, one of twelve failures and a withheld conclusion for four builds. Constant data must withhold capability; missing strength, one build and unequal subgroups must reject.
- Unit-bearing profile metadata drives upload guidance and parameter labels. Existing `cpk`/`ppk` result keys and LPBF identifiers remain compatible. UI results retain selected process, dataset/file and LSL; switching process clears the selected upload and marks older results stale.

## 11. Approved signal Pareto, investigation guidance and profiles (H-11 to H-13)

- User approved existing control-chart categories, not inspection defects: mean below X-bar LCL, mean above X-bar UCL, S above UCL. Reuse strict comparisons against the core limits; no new control rules or changes to capability formulas.
- Count each category once per build; a build can have both a mean and an S signal. Sort nonzero categories by descending count, ties in the listed order. Percent = category count / total signal occurrences * 100; cumulative percent = running count / total * 100. Report unique flagged builds separately. Empty/constant cases return zero signals and no fabricated percentages. No 80/20 or causal claim.
- Known-answer Pareto: four builds with low+spread, low, high, no signal give counts 2,1,1; percentages 50,25,25; cumulative 50,75,100; total 4 signals on 3 builds. Equality at limits is not a signal. No signals gives empty rows, total 0.
- Investigation guidance is deterministic, evidence-linked and ordered: review observed coupon failures, investigate chart signals before interpreting capability, verify no-variation/insufficient-sample cases, review stable incapability, maintain monitoring for capable data, inspect diagnostic concerns and available process logs. No automatic numerical setpoint adjustment, root-cause assertion or hardware release decision.
- Register `ebpbf` (electron beam powder bed fusion) and `laser_ded` (powder-fed laser directed energy deposition). Both reuse `build_id`, `build_date`, `uts_mpa` and the unchanged X-bar/S engine. Add three seeded scenarios each, retain all six existing CSV bytes and LPBF defaults. DED here means powder-fed laser DED, not every DED subtype.
- EB-PBF optional context: beam_current_ma (mA), accelerating_voltage_kv (kV), scan_speed_mm_s (mm/s), preheat_temperature_c (deg C), chamber_pressure_pa (Pa). Laser DED context: laser_power_w (W), powder_feed_rate_g_min (g/min), travel_speed_mm_s (mm/s), shielding_gas_flow_l_min (L/min), standoff_distance_mm (mm). Shared column names with the same unit are allowed; exclusive foreign-profile fields remain rejected. Generic columns require truthful user process selection.
- New data are clearly synthetic fixtures with documented seeds, units, collection sources and planted associations, not training data for a predictive model. One process/test population per file; no implicit unit conversion or method-derived strength limit.


## 12. Approved interactive Pareto extension (H-14)

The user approved all five recommended improvements: selectable bars linked to build details/actions, direct counts/percent/cumulative labels, a visual 80% reference, inclusive date-window views retaining full-log control limits, and a separate inspection-defect Pareto.

- Optional `primary_defect` is one recorded primary inspection category per coupon. Trim/case-normalize labels for counting; `none` explicitly means inspected with no defect; blank/missing means uninspected/unrecorded. Reject non-text labels or more than 80 characters. No inference from strength, chart flags or settings; one primary category cannot measure all defects on a multi-defect coupon.
- Inspection bars count defective inspected coupons per category; percent/cumulative denominators are defective coupons only. Report inspected, no-defect and unrecorded counts separately, plus inspection coverage. No column, no recorded inspections and all inspected/no-defect are distinct empty states. Ties are alphabetic by normalized category. Known answer porosity 2, crack 1, none 1, blank 1 gives 3 defective/4 inspected/5 total; 66.6667%,33.3333%; cumulative 66.6667%,100%; coverage 80%.
- Add four separate `*_inspection_demo.csv` files, one per process, each extending that process's unstable fixture with documented synthetic inspection results. Do not alter any original twelve CSVs or their core outputs. Each demo has 90 coupons: 39 primary defects (20 porosity,12 lack of fusion,5 cracking,2 dimensional deviation),45 explicit none,6 unrecorded; independently shuffled by fixed process seed with no physical model.
- Optional GET query / POST multipart `start_date`, `end_date`, `signal_category`, `defect_category` request a view of the same complete input. Validate ISO calendar bounds, start <= end and consistent valid source build dates when filtering. Bounds inclusive, either bound optional; reject simultaneous signal/defect selections. Clear category selection independently of the date range.
- Always analyze the complete file first. Full-log means/limits, capability indices/verdict, failure totals and diagnostics remain unchanged. Recount Pareto signals using original limits and only builds in the window; inspection counts and coverage use coupons from window builds. A bar selection narrows the investigation table/actions, not the chart denominator. Return empty states for no matching builds/categories without fabricating a new capability verdict.
- All count/percentage/range-selection logic runs in plain Python helpers; React handles formatting, SVG geometry and interactions only. Selected builds are outlined on full-log charts and listed with coupon strengths, inspection labels and recorded context. Focused actions cite their scope and retain the no-causality/no-setpoint boundary. Display 80% as a reference, not a required 80/20 relationship or evidence of severity.
- Every bar and the supporting table selection control must support keyboard activation and selected-state announcements. Keep date/filter request errors recoverable and prior results labeled. New analyses reset the view; same-origin/Connect paths and legacy no-filter requests remain compatible.


## 13. Approved documentation and interactive walkthrough (H-15)

The user requested updates to all remaining non-deployment evaluation/contract evidence and a step-by-step interactive HTML slide deck. The walkthrough teaches process/data selection, inputs, stability/capability/conformance, control charts, both Paretos, date/category investigation, uploads, diagnostics and safe experimentation. Use actual captured synthetic API outputs, clearly labeled as captured rather than live. A standalone self-contained file must work without the backend or internet; optional Open app launches the actual app separately. Downloadable example CSVs must match repository bytes. Only plot geometry/presentation are computed in JavaScript; requirement experiments use precomputed API captures. Support keyboard navigation, an outline, mobile layouts, print, knowledge checks and original-data provenance. Document missing independent human review, publication/repo synchronization and submission confirmation as open-ended remaining work, without assigning them or claiming completion. H-06 and deployment/runtime files are excluded from this increment.
