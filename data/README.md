# Synthetic titanium build logs — H-02 codebook

The original LPBF collection is described first; the [WAAM extension](#waam-extension-h-10) below documents its three supplementary files.

**Every measurement in these files is invented for software testing.** No printer, contractor,
laboratory or customer supplied these data. The values, dates, operating settings, and **895 MPa
lower specification limit (LSL)** are illustrative; they are not qualified titanium processing
settings or an aerospace acceptance specification. The LSL is entered separately in the app.

Each CSV contains **30 builds × 3 coupons = 90 coupon rows**, plus a header, with no missing
values. Builds B001–B030 occur in chronological order on September 1–30, 2026. A build's three
coupons share its date and recorded process parameters. Coupon rows are distinguished by their
position within each build; there is no separate coupon-ID column.

## Files and expected behavior

These results were computed with the existing `app/qc.py` function using LSL **895 MPa**,
`min_builds=25`, and `cpk_target=1.33`. Cpk and Ppk are dimensionless, lower-side indices.

| CSV | Behavior | Cpk | Ppk | Coupons below LSL | Flagged builds | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `stable_capable.csv` | Stable reference, strength centered near 950 MPa | 1.683472 | 1.788871 | 0/90 (0%) | 0 | capable |
| `stable_incapable.csv` | Same variation and process logs; every strength reduced by 45 MPa, centered near 905 MPa | 0.311961 | 0.331492 | 17/90 (18.888889%) | 0 | not capable |
| `unstable_shift.csv` | Reference through B019; strength drops by 35 MPa and oxygen rises by 100 ppm from B020 onward | 1.292337 | 0.711731 | 0/90 (0%) | 11 | not assessable |

Interpretation: a stable process can be insufficiently capable; an unstable process cannot receive
a capability verdict even when every observed coupon exceeds the LSL. These CSVs deliberately
separate those behaviors. Control limits are estimated from the data and are not the customer LSL.

The shifted CSV flags **B007, B014, B018, B020, B024, B025, B026, B027, B028, B029, B030**.
The planted change begins at B020, but the current core estimates limits from the **entire log**.
The changed grand mean therefore also flags some earlier builds and does not flag every changed
build. This is expected behavior of the specified implementation, not evidence that the simulated
change began early. A future fixed-baseline method would need a separate design decision. Oxygen
and strength are changed together by construction; this does not establish a causal relationship.

## Column dictionary

| Column | Type and units | Meaning | Real collection source |
| --- | --- | --- | --- |
| `build_id` | Text, no units | Printer build/job identifier, B001–B030; three consecutive rows per build | Build traveler or printer job log, linked to the tensile specimen IDs |
| `build_date` | Date, `YYYY-MM-DD` | Build date used to order the analysis; one date per build | Printer completion timestamp converted to a consistently defined local date |
| `uts_mpa` | Decimal number, MPa | Individual coupon ultimate tensile strength; one result per row | Calibrated tensile-test report: maximum tensile load divided by original specimen cross-sectional area |
| `chamber_oxygen_ppm` | Decimal number, ppm | One illustrative chamber oxygen reading per build, repeated across its coupons | Calibrated printer oxygen sensor log, summarized over an explicitly agreed build interval |
| `powder_reuse_count` | Nonnegative integer, reuse cycles | Number of powder reuse cycles assigned to the build, repeated across coupons | Powder lot/recycling records linked to the build traveler |
| `laser_power_w` | Decimal number, W | Illustrative recorded laser-power setting, repeated across coupons | Printer job recipe/settings log; distinguish commanded power from independently measured power |

The first three columns are required by the app. The last three are optional process context;
the statistics function does not read them. None of these fixtures contains nulls. Missing strength,
unequal coupon counts, one build, and zero variation are exercised in memory by `validate.py`
rather than adding invalid rows to the three demonstration files.

For real collection, use unique coupon identifiers in the source records and join them to their
build and powder lot. Define coupon orientation, specimen geometry, heat treatment, test method,
sensor aggregation interval, and equipment calibration before comparing builds. Obtain the LSL
from the actual customer specification. Preserve timestamps and traceability; do not reuse these
synthetic dates or assume the illustrative operating settings are valid production limits.

## How the files are generated

`generate.py` uses Python's standard-library `random.Random` with fixed seeds **5300** for
strength and **5301** for process context. It draws 90 independent reference strengths from a
normal distribution with mean 950 MPa and standard deviation 10 MPa, then rounds to 0.001 MPa.
There is no seed search, resampling, or filtering inside the generator. The frozen seed was
checked against the core to confirm that it gives the intended demonstration outcomes.

For each build, oxygen is drawn from Normal(40 ppm, 3 ppm), laser power from Normal(200 W, 2 W),
and powder reuse follows `(build_index - 1) % 6`. Oxygen and power are rounded to 0.001 of their
units. Every scenario shares these process readings and reference strength noise. The incapable
case applies the constant −45 MPa offset. The unstable case applies −35 MPa to strength and +100
ppm to oxygen for all coupons in B020–B030. The shifted full log is a mixture of two means; it is
not intended to satisfy a stable normal-process assumption.

## Reproduce and validate

From the repository root:

```bash
python3 data/generate.py --check  # compare CSV bytes with seeded generation, no writes
python data/validate.py          # needs app/requirements.txt installed
python demo/check.py             # H-05 scenario checks using these CSVs
```

To intentionally regenerate the three CSVs, run `python3 data/generate.py`. That overwrites these
three named files only. Use the pinned Python environment from `app/requirements.txt` for analysis;
the generator itself requires only Python's standard library. Review any output differences before
changing the frozen expected values in `validate.py` or this codebook.

The validator checks reproducible bytes, schema, finite values, valid ordered dates, 30 equal-size
builds, within-build parameter consistency, the precise planted shifts, frozen outcome numbers and
flag lists. It also checks that zero variation returns undefined capability and that one build,
unequal coupons or missing strength raise clear errors. The independent SPEC known-answer test
and other statistic tests remain in `tests/`; this task does not change the statistics implementation.

## WAAM extension (H-10)

The three LPBF files and their frozen generation above remain unchanged. A second profile adds **three synthetic WAAM files**, for six examples in total. Each WAAM file contains 30 builds W001-W030, October 1-30, 2026, and three coupons per build. They are stylized software-verification fixtures, not real titanium test results, a fitted model, or recommended production settings.

| WAAM file | Intended scenario at illustrative LSL 895 MPa | Cpk (lower) | Ppk (lower) | Failures | Flags |
| --- | --- | ---: | ---: | ---: | ---: |
| `waam_stable_capable.csv` | stable and capable | 1.911108 | 1.891083 | 0/90 | 0 |
| `waam_stable_incapable.csv` | stable, not capable | 0.307909 | 0.304683 | 18/90 | 0 |
| `waam_unstable_shift.csv` | unstable; capability conclusion withheld | 1.376709 | 0.579596 | 5/90 | 18 |

### WAAM column dictionary

| Column | Type / unit | Meaning and real collection source |
| --- | --- | --- |
| `process_type` | Text, `waam` | Selected manufacturing process; source process/job record. Optional for user uploads, but included in these fixtures. Mixed, missing or mismatched values in a supplied tag column are rejected. |
| `build_id` | Text | Build traveler identifier; repeated for each tested coupon in that build. |
| `build_date` | ISO date | Agreed build completion date from production records. |
| `uts_mpa` | Numeric MPa | Measured coupon ultimate tensile strength from a calibrated tensile-test report. |
| `arc_current_a` | Numeric A | Agreed summary of measured arc current from the welding power-source log. Distinguish measurement from commanded setpoint. |
| `arc_voltage_v` | Numeric V | Arc-voltage measurement at an agreed measurement point and time interval. |
| `wire_feed_rate_m_min` | Numeric m/min | Wire-feed measurement or recorded setpoint, provenance retained in source records. |
| `travel_speed_mm_s` | Numeric mm/s | Torch/robot travel speed from the motion log. |
| `shielding_gas_flow_l_min` | Numeric L/min | Recorded flow from a calibrated gas-flow measurement. Gas composition and shielding configuration must be retained in source records. |

Only build ID/date and strength are required; the five process measurements are optional context. LPBF fields are not required. Nonempty recognized fields from a different process profile are rejected; all-null placeholders may be omitted or left null. Extra unrelated columns do not enter the analysis. No implicit unit conversion occurs: convert mm/min to mm/s or m/min explicitly before upload and retain collection provenance.

Parameter choices and units are informed by published experimental reporting, including [the titanium pulsed-arc WAAM study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11442374/) and [the hot-wire titanium study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7962131/). These references support the measurement vocabulary only. We do not borrow their acceptance criteria, recommend their settings, or represent the generator's associations as their findings.

### WAAM generation and independent checks

`generate_waam.py` uses seed **5302** for 90 independent normal draws with mean 960 MPa and standard deviation 12 MPa, rounded to 0.001 MPa, grouped consecutively into three coupons per build. Seed **5303** generates optional process context. The stable reference has Shapiro-Wilk p = 0.309038; this diagnostic does not prove normality. Independent sample-SD arithmetic checks validate the outputs. These illustrative distributions do not model real coupon correlations or manufacturing variability; do not infer actual production defect probabilities from them.

The incapable case subtracts 55 MPa from every reference strength. From W020 onward the unstable case subtracts 50 MPa and 5 L/min from the reference strength and shielding-gas flow. All other values remain identical. The association is planted for investigation demonstration, not a causal model. Full-log limits flag 18 builds: W003, W004, W005, W010, W014, W016, W017 and W020-W030. The late strength shift moves the center line, so earlier reference builds can also fall outside retrospective limits. These are not prospective limits frozen from a stable qualification baseline.

Synthetic baseline parameter distributions are independent uniform jitter around 125 A (+/-4), 12 V (+/-0.4), 1.5 m/min (+/-0.08), 4 mm/s (+/-0.2), and 18 L/min (+/-0.8). All are illustrative and require replacement with measured or qualified records for engineering use. Build parameters repeat across the three coupon rows. Cpk uses within-build sample SDs corrected by c4; Ppk uses the overall sample SD, so their estimates can differ even for this stable reference.

From the repository root (use the project's Python executable in PowerShell):

```powershell
.\.venv\Scripts\python.exe data/generate_waam.py --check
.\.venv\Scripts\python.exe data/validate_waam.py
```

The generator writes only its three named WAAM files when `--check` is omitted. The validator checks byte reproduction, schema, units-as-column-contract, grouping, tags, dates, frozen outcomes and shift location. It independently checks arithmetic with Python's standard-library sample SD and the closed form c4=sqrt(pi)/2 for n=3; it does not treat matching the core alone as proof of correctness. Original `generate.py --check` and `validate.py` remain the LPBF checks.

For either process, real capability assessment requires justified rational subgroups, comparable alloy/orientation/post-processing/testing conditions and a suitable measurement system. Do not pool different processes or test populations. Process selection does not predict strength, qualify a welding procedure, or certify a bracket.


## EB-PBF and powder-fed laser DED (H-13)

Six supplementary files extend the original LPBF and WAAM examples, which are unchanged. All files below contain **synthetic** data: 30 builds with three coupons each. Strength in MPa is measured input to the app, not predicted output. Example LSL 895 MPa is illustrative, not an aerospace standard. These fixtures are not training/test partitions for a learned manufacturing model.

| File | Cpk | Ppk | Below LSL | Unique flagged builds | Signal occurrences | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `ebpbf_stable_capable.csv` | 2.542353 | 2.267525 | 0/90 | 0 | 0 | capable |
| `ebpbf_stable_incapable.csv` | 0.402748 | 0.359211 | 16/90 | 0 | 0 | not capable |
| `ebpbf_unstable_shift.csv` | 1.757831 | 0.535751 | 4/90 | 24 | 24 | not assessable |
| `laser_ded_stable_capable.csv` | 1.394480 | 1.423374 | 0/90 | 0 | 0 | capable |
| `laser_ded_stable_incapable.csv` | 0.231754 | 0.236557 | 22/90 | 0 | 0 | not capable |
| `laser_ded_unstable_shift.csv` | 0.863484 | 0.444494 | 12/90 | 15 | 16 | not assessable |

Each row contains `process_type` (`ebpbf` or `laser_ded`), `build_id` (E001-E030 or D001-D030), `build_date` (ISO 2026-10-01 through 2026-10-30), `uts_mpa` (numeric MPa) and the selected profile's five optional numeric context columns. Coupon rows repeat build-level process context. Required build/date/UTS semantics are the same as the original codebook. Optional context never changes core strength statistics.

| Process | Optional column | Units | Real collection source |
| --- | --- | --- | --- |
| EB-PBF | `beam_current_ma` | mA | Electron-beam power-source log |
| EB-PBF | `accelerating_voltage_kv` | kV | Electron-beam power-source log |
| EB-PBF | `scan_speed_mm_s` | mm/s | Build scan/motion log |
| EB-PBF | `preheat_temperature_c` | deg C | Recorded preheat/thermal measurement, with sensor definition |
| EB-PBF | `chamber_pressure_pa` | Pa | Chamber vacuum-gauge record |
| Powder-fed laser DED | `laser_power_w` | W | Laser power log |
| Powder-fed laser DED | `powder_feed_rate_g_min` | g/min | Calibrated powder feeder log |
| Powder-fed laser DED | `travel_speed_mm_s` | mm/s | Motion controller log |
| Powder-fed laser DED | `shielding_gas_flow_l_min` | L/min | Gas flow record |
| Powder-fed laser DED | `standoff_distance_mm` | mm | Nozzle-to-workpiece distance record |

For real data, link coupon tensile reports to build travelers, material lot, orientation, post-processing and test method. Keep one comparable population and a defensible equal-size rational subgroup per build. Sensor location, calibration and aggregation matter; these field labels alone do not define a qualified measurement procedure. Shared fields retain identical units across profiles; no implicit conversion occurs.

### Reproduction and constructed signals

`generate_additional.py` uses Python `random.Random` seeds fixed before inspecting outputs: EB-PBF strength 5304, context 5305; laser DED strength 5306, context 5307. EB-PBF reference strengths are 90 independent normal draws with mean 970 and SD 14 MPa; laser DED mean 960 and SD 15 MPa. Round strengths to 0.001 MPa and group consecutive triples. Reference Shapiro-Wilk p-values are 0.600812 and 0.716425 respectively; neither proves normality.

Context uses independent uniform jitter, rounded to four decimals, around these illustrative centers/spreads in table-column order: EB-PBF `(12 +/-1, 60 +/-1, 1000 +/-50, 700 +/-15, 0.02 +/-0.004)`; laser DED `(1000 +/-40, 6 +/-0.3, 8 +/-0.4, 20 +/-1, 12 +/-0.5)`. They are not recommended settings, validated operating windows or values copied from a study.

The EB-PBF incapable fixture subtracts 65 MPa from every reference coupon; laser DED subtracts 55 MPa. Unstable EB-PBF subtracts 65 MPa strength and 80 deg C preheat from E020; unstable laser DED subtracts 55 MPa strength and 1 g/min powder feed from D020, with additional strength offsets `[-60, 0, +60]` on D024's three coupons. This deliberately plants a within-build spread increase while preserving that build's mean. All other values remain the reference values. Associations are constructed for the demo and do not establish physical causality or settings-to-strength effects.

With whole-log limits, EB-PBF signals include 13 high means (E003-E009, E012, E014-E016, E018-E019) and 11 low means (E020-E030). Laser DED has 10 low means (D020-D026, D028-D030), 5 high means (D005-D006, D009, D014, D019) and one high S (D024). D024 appears twice: 16 signals on 15 builds. Full-log limits shift with the excursion and can flag earlier reference builds; these are not limits frozen from a qualified stable baseline.

```powershell
.\.venv\Scripts\python.exe data/generate_additional.py --check
.\.venv\Scripts\python.exe data/validate_additional.py
```

Without `--check`, the generator writes only its six named new files. The validator checks byte reproduction, schemas, grouping, dates, tags, context consistency, frozen outcomes and planted changes. Independent Python stdlib sample SDs, c4=sqrt(pi)/2 for n=3, chart-limit arithmetic, coupon failures and category counts cross-check the core.

Parameter vocabulary is informed by primary sources: [Wang et al., EB-PBF thermal modelling](https://pmc.ncbi.nlm.nih.gov/articles/PMC8658374/), [NIST EB-PBF powder/preheating study](https://www.nist.gov/publications/sintered-powder-oxidation-variation-function-build-height-titanium-alloy-produced) and [NIST directed energy deposition research](https://www.nist.gov/additive-manufacturing/research-areas/technologies/directed-energy-deposition). These sources motivate recorded context, not the illustrative numeric distributions, thresholds or causal claims.


## Synthetic inspection examples (H-14)

Four additional runnable files preserve every original strength/setting field and append optional `primary_defect`. All records are **synthetic**, including every inspection outcome; no real inspection or calibrated inspection performance is implied. Original twelve CSV bytes and their generators are unchanged.

| New file | Strength/settings source | Inspection shuffle seed |
| --- | --- | ---: |
| `lpbf_inspection_demo.csv` | `unstable_shift.csv` | 5310 |
| `waam_inspection_demo.csv` | `waam_unstable_shift.csv` | 5311 |
| `ebpbf_inspection_demo.csv` | `ebpbf_unstable_shift.csv` | 5312 |
| `laser_ded_inspection_demo.csv` | `laser_ded_unstable_shift.csv` | 5313 |

Each has 90 coupon rows and exactly **20 Porosity, 12 Lack of fusion, 5 Cracking, 2 Dimensional deviation, 45 `none`, and 6 blank** primary-defect fields. Python `random.Random(seed).shuffle` assigns this fixed inventory independently to source rows. Categories and their associations with builds/strength are invented for demonstration, not empirical frequencies, process physics or a model trained on settings. The labels do not prove those conditions were observed in the source strength data.

The one extra variable, `primary_defect`, is text (no physical units), one primary classification per coupon. A real source would be a traceable coupon inspection report, with the inspection method, coverage, detection limits, classification criteria and responsible reviewer recorded outside this minimal example. If a coupon has several defects, define a documented primary-category rule or use a future separate multi-defect event schema; do not put a list of events into this primary field and count it as multiple coupons.

`none` explicitly means inspected/no primary defect recorded; matching ignores case and surrounding whitespace. A blank means no inspection result recorded, not a pass. A missing column also means no supplied inspection information. Other recorded labels are counted case-insensitively, with at most 80 characters per label. The API preserves literal `None`/`none` as text for this field instead of allowing pandas to turn the reserved no-defect value into a missing value. No inspection outcome is inferred from measured UTS or chart flags.

Full-window inspection totals are 84 inspected, 39 defective, 45 explicit no-defect and 6 unrecorded. Coverage = 84/90 = 93.3333%. The defect Pareto denominator is 39: counts 20,12,5,2; percentages 51.2821%,30.7692%,12.8205%,5.1282%; cumulative 51.2821%,82.0513%,94.8718%,100%. Those are recorded primary categories only; they are not strength-failure rates or an inventory of every possible defect. The 80% line is a visual reference, not an asserted 80/20 law or a severity threshold.

The new files have the same core verdict/indices/failure counts as their source unstable scenario at illustrative LSL 895 MPa. LPBF source dates differ from the October dates in the other process fixtures; choose actual dates from each source. Optional inclusive date views change Pareto denominators and inspection coverage only for window builds while keeping complete-file control limits and capability results fixed. Original 1-based data-row numbers (excluding header) identify selected coupon records even after filtering.

```powershell
.\.venv\Scripts\python.exe data/generate_inspection.py --check
.\.venv\Scripts\python.exe data/validate_inspection.py
```

Without `--check`, generation writes only the four new named files. Validation checks byte reproduction, unchanged source columns, independent category counts, coverage, cumulative arithmetic and exact core-output equality. All four datasets appear as **Inspection defect example** under their process selector; all previous dataset IDs remain available. There are now sixteen files, four per process. See the [interaction and API contract](../docs/pareto-explorer.md).
