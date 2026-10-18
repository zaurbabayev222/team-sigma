# AeroQual
## Technology-Agnostic Titanium Additive Manufacturing Quality Dashboard

**Cornell SYSEN 5300 — Six Sigma Hackathon**  
**Status:** Proposed / in development  
**Initial demonstration:** Synthetic laser powder bed fusion (LPBF) data; LPBF is **not** a requirement of the original problem.

## Executive summary

AeroQual is an interactive process-monitoring and quality-analysis dashboard for aerospace contractors manufacturing 3D-printed titanium brackets. The customer problem is failed strength testing and insufficient linkage between manufacturing conditions, material defects, and final part performance. AeroQual combines statistical process control (SPC), process capability, yield tracking, and exploratory root-cause analysis to help engineers determine whether a manufacturing process is stable, whether it is capable of meeting applicable customer specifications, and what conditions merit investigation.

The platform is **technology-agnostic**: a common data model and statistical engine operate across metal additive manufacturing methods, while optional, validated process profiles define method-specific measurements. The initial demonstration uses LPBF only to provide a concrete, reproducible example. No universal titanium strength threshold or printing parameter limit is implied.

## Problem statement and objectives

An aerospace contractor 3D-printing titanium brackets is failing client strength tests. Its current records do not adequately connect environmental and process conditions to final strength and defects. The dashboard must:

1. Track tested-part and build-level conformance to **customer-provided** requirements.
2. Detect special-cause process variation through appropriate SPC methods.
3. Assess process capability only where sufficient stable data and defensible variance estimates exist.
4. Explore associations between process parameters, defect characteristics, and mechanical properties.
5. Support traceable engineering investigation and corrective action without automatically certifying or releasing hardware.

## Manufacturing-process support

| Process profile | Example process-specific inputs | Notes |
|---|---|---|
| LPBF — initial demo | Laser power, scan speed, hatch spacing, layer thickness, chamber oxygen, powder reuse | Illustrative implementation only |
| Electron beam powder bed fusion (EB-PBF) | Beam current/power, scan speed, vacuum pressure, build temperature | Do not require laser power or chamber oxygen fields |
| Directed energy deposition (DED) | Energy-source power, feedstock feed rate, travel speed, shielding conditions | May use powder or wire feedstock |
| Wire arc additive manufacturing (WAAM) | Arc current, voltage, wire feed rate, travel speed, shielding gas | Does not use a powder bed |
| Binder jetting with sintering | Binder saturation, green density, furnace profile, shrinkage | Different consolidation and defect mechanisms |

The system shall permit a `process_type` and a process-profile configuration, including parameter name, unit, type, expected collection method, and optional **customer-validated** operating window. Unsupported fields remain absent or null, never silently set to zero. New process profiles can be added without rewriting the statistical engine.

## Data architecture

### Common traceability fields

`observation_id`, `part_id`, `build_id`, `machine_id`, `process_type`, `material_alloy`, `material_lot`, `timestamp`, `specification_id`, `test_method`, `specimen_orientation`, `post_processing_batch`, `inspection_method`.

### Common outcome and inspection fields

- Ultimate tensile strength (UTS), MPa
- Yield strength, MPa
- Elongation at break, %
- Porosity, %, when measured
- Dimensional deviation, mm, when measured
- Residual stress, MPa, when measured or estimated with method indicated
- Customer acceptance results and disposition, with provenance

### Process-specific measurements

Store as typed, unit-bearing parameter observations linked to a build or part, or as validated process-profile-specific fields. For the LPBF demonstration, use laser power (W), scan speed (mm/s), hatch spacing (mm), layer thickness (µm), chamber oxygen (ppm), and powder reuse count. Other methods should not inherit these as mandatory inputs.

Record measurement timestamps and whether a parameter was measured, commanded, estimated, or derived. Track missingness explicitly. Where LPBF volumetric energy density is calculated, use `P / (v * h * t)` with layer thickness converted to mm; label it a derived proxy, not a universal strength predictor.

### Statistical unit of analysis

Distinguish **coupon/test**, **part**, and **build**. Multiple coupons from the same build are correlated; do not treat them as independent builds. Define aggregation, grouping, test coverage, and the denominator for each quality metric. A missing required test is not a pass.

## Statistical engine

| Method | Implementation | Interpretation |
|---|---|---|
| Descriptive statistics | Mean, median, SD, quantiles, missingness | Baseline variation and data completeness |
| SPC | Individuals–moving range (I-MR) for appropriately ordered individual results; X-bar/R only for defensible rational subgroups | Detect statistical instability; control limits are **not** specifications |
| Process capability | Cp/Cpk for two-sided specifications; Cpl/Cpu for one-sided; Pp/Ppk or corresponding one-sided overall indices | Only assign a positive capability verdict when stability, data sufficiency, and measurement assumptions are satisfied |
| Conformance and yield | Tested-part failure rate, first-pass yield, build-level review status, with explicit denominators | Keep conformance separate from statistical capability |
| Relationships | Pearson/Spearman correlations; multivariable regression, confidence intervals, diagnostics | Associations, not causal proof; control for machine, lot, process type, and clustered observations where appropriate |
| Factor comparison | ANOVA or grouped comparisons when design and assumptions support them | Compare machines, lots, orientations, and parameter settings |
| Investigation | Rule-based deviation review and optional FMEA prioritization | Engineer-review hypotheses and documented corrective actions |

For a lower-only strength specification, report `Cpl = (mean − LSL)/(3 × within_sigma)` and the corresponding overall index `(mean − LSL)/(3 × overall_sigma)`. Never fabricate an upper strength limit to force a two-sided Cpk. Capability criteria, minimum sample size, and approved limits are configurable, not hard-coded as aerospace standards.

## Dashboard modules

### 1. Production overview

Process-profile selector; dataset/scenario selector; yield, failure, missing-test, and alert counts; filters by machine, build, material lot, and date; traceable build table. Prominent **SYNTHETIC DEMO DATA** banner when appropriate.

### 2. Stability and capability

Control charts, specification distributions, one-sided/two-sided capability indices, explicit sample-size and stability assessments, and reasons for withholding capability conclusions.

### 3. Relationships and root-cause exploration

Process-specific scatterplots, correlation and regression summaries, effect uncertainty, group comparisons, and confounding warnings. Variables available for analysis depend on the selected process profile.

### 4. Build investigation

Build/part traceability, test outcomes, process-parameter excursions, inspection findings, suggested investigation checklist, evidence notes, and disposition status. Alerts are not automated airworthiness or customer acceptance decisions.

## Synthetic demonstration scenarios

Generate three reproducible LPBF example datasets, with fixed seeds and documented assumptions:

1. **Stable and capable:** Sufficient observations, in-control variation, and adequate lower-specification strength capability.
2. **Stable but incapable:** Statistically stable measurements that fail the chosen capability criterion.
3. **Unstable:** Time-ordered process shift or special cause, with relevant process deviations and an explicit warning that capability conclusions are unreliable.

Use multiple builds, machines, lots, and repeated coupon observations. The synthetic relationships should be plausible enough for demonstration, but **must not be represented as empirically validated physics**. All limits (including example UTS and oxygen values) are illustrative and replaceable.

## Architecture and deliverables

- **Frontend:** React, Vite, TypeScript, Recharts; responsive dashboard and clear units.
- **Backend:** Python FastAPI with pandas, NumPy, SciPy, and statsmodels.
- **Data:** CSV ingestion, schema validation, process-profile registry, three generated synthetic datasets.
- **Quality:** Unit tests for capability/SPC calculations, expected-scenario tests, API tests, frontend build checks, and a data dictionary.
- **Documentation:** Local Windows/Positron setup, API endpoints, assumptions, limitations, and a deployment plan for Posit Connect subject to actual platform verification.

## Safety and interpretation boundaries

AeroQual is a decision-support prototype. Passing an observed test does not prove process capability; statistical capability does not automatically qualify aerospace hardware. The application does not replace approved material specifications, test standards, measurement-system analysis, qualification plans, customer acceptance processes, or engineering sign-off. Do not imply that LPBF is required by the project prompt.

## Roadmap

1. Implement process-agnostic schema and process-profile registry.
2. Build the LPBF demonstration generator and validate three scenarios.
3. Implement and test statistical calculations.
4. Expose the analysis through FastAPI.
5. Build and integrate the four dashboard modules.
6. Validate, document, and prepare deployment.

**Project vision:** Convert additive manufacturing process and test data into traceable, statistically defensible engineering insight, across titanium 3D-printing technologies.
