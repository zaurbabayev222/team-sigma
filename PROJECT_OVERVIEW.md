# AeroQual
## Titanium Additive Manufacturing Quality Dashboard

**Cornell SYSEN 5300 — Six Sigma Hackathon** · Team **Sigma Airlines** · Virtual DL Challenge (7 days)
**Prompt:** 1, "Industrial Systems, 3D Printing for Aerospace"
**Status:** Release 1 scope agreed 2026-10-19; in development
**Initial demonstration:** synthetic laser powder bed fusion (LPBF) data. LPBF is **not** a requirement of the prompt.

> This overview is the big picture. The binding definition of release 1 is [`SPEC.md`](SPEC.md); the
> reasons behind each choice are in [`docs/decisions.md`](docs/decisions.md).

## Executive summary

AeroQual is a process-monitoring and capability dashboard for aerospace contractors 3D-printing
titanium brackets. The customer problem is failed strength tests and records that do not link
process conditions to final part strength.

Release 1 answers three questions for one user, the quality engineer who reviews each finished
build:

1. **Is the printing process stable,** or did a build shift? (X-bar and S chart, one subgroup per build)
2. **Can the process reliably meet the customer's minimum strength?** (lower-side Cpk and Ppk)
3. **How often do coupons fail today?** (coupon failure rate)

When builds are flagged, the tool shows which recorded process parameters moved, so the engineer
knows where to look first.

The platform is designed to be **technology-agnostic**: the statistics never know which printing
process produced the data, and each process is described by one small *process profile*. Release 1
ships the LPBF profile only; other processes are added later as new profiles.

## Problem statement and objectives

An aerospace contractor 3D-printing titanium brackets is failing client strength tests. Its records
do not adequately connect process and environmental conditions to final strength. The tool must:

1. Track coupon-level conformance to the **customer-provided** minimum strength.
2. Detect special-cause variation between builds with an appropriate control chart.
3. Assess capability only when the process is stable and there is enough data, and say why when not.
4. Point to process parameters associated with flagged builds.
5. Support engineering investigation without automatically certifying or releasing hardware.

## Release 1 at a glance

| Area | Release 1 |
|---|---|
| User | The contractor's quality engineer reviewing tensile-test results per finished build |
| Process | LPBF only, through one process profile |
| Required inputs | `build_id`, `build_date`, `uts_mpa` per coupon, customer minimum strength (LSL, MPa) |
| Optional inputs | `chamber_oxygen_ppm`, `powder_reuse_count`, `laser_power_w` |
| Statistics | X-bar and S chart by build; Cpk and Ppk (lower side); coupon failure rate; verdict |
| Verdict | "not assessable" if a build is flagged or fewer than 25 builds; else "capable" if Cpk ≥ 1.33 (a setting); else "not capable" |
| Delivery | FastAPI (Python) backend + React (Vite, plain JavaScript) dashboard, deployed on Posit Connect |
| Data | Three synthetic datasets, 30 builds × 3 coupons, fixed seeds, with a codebook |

## Statistical engine

The engine is one plain, tested Python module (`app/qc.py`). It takes generic inputs only: a
subgroup id (the build), an order (the build date), a measured value (tensile strength) and a lower
limit. Full formulas and a hand-worked known-answer example are in SPEC section 4.

| Method | Implementation | Interpretation |
|---|---|---|
| SPC | X-bar and S chart; each build's coupons are one subgroup; limits from the average within-build standard deviation | Flags builds that shifted or varied unusually; control limits are **not** specifications |
| Capability | Cpk (lower) from short-term σ = s̄/c4; Ppk (lower) from the standard deviation of all coupons | Only a stable process with enough builds gets a "capable" verdict |
| Conformance | Coupons below the minimum ÷ all coupons | What the customer sees today; kept separate from capability |
| Investigation | For flagged builds, each optional parameter's value next to its usual range | A lead to investigate, not proof of cause |

Safeguards kept from the original plan:

- Strength has a minimum only: report lower-side Cpk and Ppk, and never invent an upper limit.
- Coupons from one build are not independent: builds are the subgroups, so within-build and
  between-build variation are measured separately.
- A missing test is not a pass: a blank strength value is an error naming the row.
- Capability thresholds and minimum sample size are settings, not hard-coded aerospace standards.
- Coupon strengths are checked for rough normality (histogram plus Shapiro-Wilk p-value).

## Expandable design: process profiles

```text
CSV upload -> process profile -> statistics (app/qc.py) -> FastAPI -> React page
              (app/profiles/lpbf.py:          (generic: subgroup, order,
               optional parameters,            value, lower limit)
               units, labels)
```

- A **process profile** is one small Python file listing that process's optional parameters, each
  with a name, unit and label.
- The page builds its parameter table from the profile, so a new profile needs no front-end change.
- **To add a process later:** write `app/profiles/<process>.py`, add a test dataset for it, and
  register its name. The statistics and their tests do not change.

| Process profile | Example optional parameters | Status |
|---|---|---|
| LPBF | Laser power, chamber oxygen, powder reuse | Release 1 |
| Electron beam powder bed fusion (EB-PBF) | Beam power, scan speed, vacuum pressure, build temperature | Future profile |
| Directed energy deposition (DED) | Energy-source power, feed rate, travel speed, shielding | Future profile |
| Wire arc additive manufacturing (WAAM) | Arc current, voltage, wire feed rate, travel speed | Future profile |
| Binder jetting with sintering | Binder saturation, green density, furnace profile | Future profile |

Unsupported fields stay absent, never silently set to zero.

## Dashboard

Release 1 is one page:

- Dataset selector and the customer minimum (LSL) input, with a **SYNTHETIC DEMO DATA** banner.
- X-bar and S charts of tensile strength (MPa) by build, flagged builds in red.
- Cpk, Ppk and failure rate, with the verdict and its reason.
- Parameter table for flagged builds, when the optional columns are present.

## Synthetic demonstration scenarios

Three reproducible LPBF datasets, each 30 builds × 3 coupons, fixed seeds, documented in
`data/README.md`:

1. **`stable_capable.csv`:** in control, Cpk ≥ 1.33.
2. **`stable_incapable.csv`:** in control, but the mean sits too close to the minimum, Cpk < 1.33.
3. **`unstable_shift.csv`:** chamber oxygen rises from build 20 and strength drops; builds are
   flagged and the verdict is "not assessable".

The relationships are plausible for demonstration but **not** empirically validated physics. All
limits, including example strength and oxygen values, are illustrative and replaceable.

## Roadmap

| Phase | What | Status |
|---|---|---|
| Release 1 | The scope above, deployed with a public URL | In development |
| Later | Correlation of each parameter with strength; confidence intervals for Cpk and Ppk | After release 1 passes review |
| Later | Traceability columns (machine, lot, heat treatment, orientation) and filters | Optional columns, no engine change |
| Later | Two-sided Cpk on dimensional deviation (an upper limit input) | Engine extension |
| Later | Unequal coupons per build | Engine extension (per-build constants) |
| Later | Other process profiles (EB-PBF, DED, WAAM, binder jetting) | New profile files |
| Later | Regression, ANOVA, FMEA prioritization | Only with a clear use case |

## Safety and interpretation boundaries

AeroQual is a decision-support prototype. Passing an observed test does not prove process
capability, and statistical capability does not qualify aerospace hardware. The tool does not
replace approved material specifications, test standards, measurement-system analysis,
qualification plans, customer acceptance or engineering sign-off. LPBF is a demonstration choice,
not a requirement of the prompt.

**Project vision:** turn additive manufacturing process and test data into traceable, statistically
defensible engineering insight, across titanium 3D-printing technologies.
