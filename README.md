# AeroQual

Titanium additive manufacturing quality dashboard by **Sigma Airlines**, Cornell SYSEN 5300 Six Sigma Hackathon, Virtual DL Challenge.

AeroQual helps a quality engineer review tensile-test coupons after each build: detect changes in process stability, assess lower-side strength capability, count observed failures, and inspect recorded conditions for flagged builds. The application supports **laser powder bed fusion (LPBF)** and **wire arc additive manufacturing (WAAM)**, **electron beam powder bed fusion (EB-PBF)** and **powder-fed laser DED** profiles through a React/Vite dashboard and FastAPI backend. Python calculates every QC result.

**Live app (public, no login):** [https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/](https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/) opens the dashboard; the API is at `/docs`.

**Status:** the dashboard, API and sixteen synthetic datasets (four per process) are deployed on the course Posit Connect server and verified logged out on October 22, 2026. Independent fresh-clone teammate reproduction is still open. This prototype does not certify hardware or authorize release. All demonstration data and example limits are synthetic or illustrative.

Start with the **[interactive HTML walkthrough](demo/slidedeck/index.html)** or the
[written demo](demo/README.md). Download the HTML file and open it directly in a browser;
GitHub's file view shows its source. The 14 lessons include captured synthetic API results,
downloadable example CSVs, chart/Pareto exercises and requirement experiments. It works offline;
use the running dashboard for actual uploads and analysis.

[Evaluation evidence](docs/evaluation.md) maps the unchanged 100-point rubric.
[Remaining work](docs/remaining-work.md) is an open-ended handoff with no new assignments;
[submission.md](docs/submission.md) provides draft submission text. The user approved publishing this
candidate to main. Local test success does not establish independent acceptance, deployment or submission.

## Run in Positron on Windows PowerShell

Open this repository folder in Positron and use its PowerShell terminal, starting in the repository root. Install Python and Node.js/npm first. Deployment targets Python **3.12** and Node **22**; local preview also succeeded with Python **3.13.15** and Node **24.20.0**. Internet access is required for uncached dependencies. Check availability with `python --version`, `node --version`, and `npm.cmd --version`.

First-time setup (no virtual-environment activation or execution-policy change needed):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r app/requirements.txt
npm.cmd --prefix app/frontend ci --no-audit --no-fund
Copy-Item -Path data/*.csv -Destination app/data/
npm.cmd --prefix app/frontend run build
```

Start both the API and built dashboard with one command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.app:app --host 127.0.0.1 --port 8000
```

Keep the terminal running. Open **[the dashboard](http://127.0.0.1:8000/dashboard/)**. [API documentation](http://127.0.0.1:8000/docs) provides interactive requests; [health](http://127.0.0.1:8000/health) returns `{"status":"ok"}`. Stop with `Ctrl+C`. On subsequent starts, use only the launch command unless files changed. Rebuild after frontend changes and repeat the copy after dataset changes.

If Node is installed in its usual Windows location but is missing from PATH, reopen Positron or set it for this terminal session:

```powershell
$env:Path = 'C:\Program Files\nodejs;' + $env:Path
```

### Bash alternative

On Linux/macOS or configured Git Bash, with Python and npm on PATH:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
bash app/testme.sh
```

`testme.sh` copies datasets, runs `npm ci`, builds React and starts Uvicorn on port 8000. It requires Bash; Windows PowerShell alone cannot execute it. It binds all local interfaces; the PowerShell command above binds loopback only.

## Use the dashboard

1. Select **Printing process** (LPBF, WAAM, EB-PBF or laser DED), then **Stable and capable**, **Stable but not capable**, **Unstable process shift**, or **Inspection defect example**, or upload your coupon CSV. An upload takes precedence; use **Clear upload** to return to examples. Changing process clears the upload and marks previous results stale.
2. Enter **Minimum strength, LSL (MPa)** from the customer specification. The demo default **895 MPa** is illustrative, not a titanium acceptance standard.
3. Click **Analyze builds**. Review the labeled dataset/file and LSL, then read the separate stability, capability and observed-failure summaries. Expand the full backend reason when needed.
4. Inspect X-bar/S charts, the **Control-chart signal Pareto**, **Recommended investigation actions** and the combined **Build investigation** table. Hover or keyboard-focus a chart point; **View all build data** exposes every plotted value. Expand diagnostics, observed reference ranges or distribution bins for supporting detail.
5. If you change an input, the page labels the previous results and asks you to analyze again. Inputs lock while a request is running; failed analyses display an error with recovery guidance.

The dashboard uses defaults of 25 builds and Cpk target 1.33. These settings are configurable through the API, not dashboard controls. Red squares identify builds flagged by either chart; circles represent unflagged builds. The table explains each flag. Chart and table containers scroll horizontally on small screens.

## Inputs and parameters

The CSV has one row per tested coupon. Select the process that produced it; do not mix processes, alloys, orientations or post-processing/test populations. Keep comparable test conditions and one consistent ISO date per build.

| CSV column | Required | Units / format | Source |
| --- | --- | --- | --- |
| `build_id` | Yes | Text, shared by coupons in the build | Build traveler |
| `build_date` | Yes | `YYYY-MM-DD` | Build log |
| `uts_mpa` | Yes | Finite numeric MPa | Tensile-test report |
| `chamber_oxygen_ppm` (LPBF) | No | Numeric ppm | Printer log |
| `powder_reuse_count` (LPBF) | No | Nonnegative integer count | Powder record |
| `laser_power_w` (LPBF) | No | Numeric W | Printer settings |
| `arc_current_a` (WAAM) | No | Numeric A | Welding log |
| `arc_voltage_v` (WAAM) | No | Numeric V | Welding log |
| `wire_feed_rate_m_min` (WAAM) | No | Numeric m/min | Wire feeder log |
| `travel_speed_mm_s` (WAAM) | No | Numeric mm/s | Motion controller log |
| `shielding_gas_flow_l_min` (WAAM) | No | Numeric L/min | Gas flow record |
| `primary_defect` | No | Text: recorded primary inspection category; `none` for inspected/no defect, blank for unrecorded | Coupon inspection report |
| `process_type` | No | `lpbf`, `waam`, `ebpbf` or `laser_ded`, matching the selection on every row | Manufacturing record |

EB-PBF and laser DED optional fields, units and collection sources are in the [expanded codebook](data/README.md#eb-pbf-and-powder-fed-laser-ded-h-13).

At least two builds and two coupons per build are required, with equal coupon counts across builds. Blank, nonnumeric or infinite strength values cause an error, never a pass. Optional parameters are descriptive and do not affect capability. Unrecognized extra columns are not analyzed; nonempty recognized fields from the other process are rejected.

| Separate parameter | Required | Default | Meaning |
| --- | --- | --- | --- |
| `process_type` | No in API; select in dashboard | `lpbf` | Manufacturing process: `lpbf`, `waam`, `ebpbf` or `laser_ded` |
| `lsl` | Yes | None in API; 895 in dashboard | Customer lower strength limit, MPa |
| `min_builds` | No | 25 | Minimum builds for a capability verdict |
| `cpk_target` | No | 1.33 | Configured lower-side Cpk target |

Supply a positive integer `min_builds` and meaningful positive `cpk_target`; current code does not enforce those domain bounds. Dates are sorted as strings using the first date per build. Valid ISO dates, consistent dates, nonblank identifiers and correct units remain caller responsibilities. See [the codebook](data/README.md) and [API/function reference](app/README.md).

## Synthetic demonstration

Each file contains **30 builds with 3 coupons each (90 total)**. Live API checks with LSL 895 MPa and default settings reproduce:

| Dataset | Cpk (lower) | Ppk (lower) | Failures | Flagged builds | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `stable_capable` | 1.683472 | 1.788871 | 0/90 | 0 | capable |
| `stable_incapable` | 0.311961 | 0.331492 | 17/90 | 0 | not capable |
| `unstable_shift` | 1.292337 | 0.711731 | 0/90 | 11 | not assessable |
| `waam_stable_capable` | 1.911108 | 1.891083 | 0/90 | 0 | capable |
| `waam_stable_incapable` | 0.307909 | 0.304683 | 18/90 | 0 | not capable |
| `waam_unstable_shift` | 1.376709 | 0.579596 | 5/90 | 18 | not assessable |
| `ebpbf_stable_capable` | 2.542353 | 2.267525 | 0/90 | 0 | capable |
| `ebpbf_stable_incapable` | 0.402748 | 0.359211 | 16/90 | 0 | not capable |
| `ebpbf_unstable_shift` | 1.757831 | 0.535751 | 4/90 | 24 | not assessable |
| `laser_ded_stable_capable` | 1.394480 | 1.423374 | 0/90 | 0 | capable |
| `laser_ded_stable_incapable` | 0.231754 | 0.236557 | 22/90 | 0 | not capable |
| `laser_ded_unstable_shift` | 0.863484 | 0.444494 | 12/90 | 15 | not assessable |

Stability alone does not establish capability; zero observed failures alone does not establish capability. In the unstable example, strength and oxygen changes are planted together from B020. Their association is synthetic, not validated manufacturing physics.

WAAM optional context uses `arc_current_a` (A), `arc_voltage_v` (V), `wire_feed_rate_m_min` (m/min), `travel_speed_mm_s` (mm/s), and `shielding_gas_flow_l_min` (L/min). These are descriptive measurements, not a strength-prediction model. LPBF optional fields in the table above are not required for WAAM. An optional CSV `process_type` column must consistently match the selection; nonempty known fields from the other process are rejected. Generic three-column files rely on the user's process declaration. Units must match the column names; no implicit conversion occurs.

The [complete walkthrough](demo/README.md) provides a three-minute judging sequence, local desktop/mobile captures, exact chart limits, flags, parameters and interpretation. Its Windows commands use the same environment as this README.

## Interpret the statistics

Each build is a subgroup. X-bar monitors build means; S monitors within-build sample SD. Limits are estimated from the **whole submitted file**, without a separately approved baseline. A mean outside X-bar limits or S above its upper limit flags a build. Lower S-limit violations and run/trend rules are not implemented.

Lower-side `cpk` uses within-build sigma estimated as average build SD divided by c4. Lower-side `ppk` uses overall coupon sample SD. These correspond to Cpl/Ppl terminology; the existing interface retains Cpk/Ppk labels. There is no fabricated upper strength limit. Failure rate counts coupons strictly below LSL; equality passes.

Verdict precedence is **not assessable** for undefined variation, then any flagged build, then too few builds; otherwise **capable** when Cpk meets the target, or **not capable**. Numeric indices may still appear for unstable data and are not an approval.

Interpretation assumes meaningful build subgroups, comparable approximately normal strengths and a suitable measurement system. The pooled Shapiro-Wilk p-value is diagnostic only: it does not prove normality or gate the verdict. Repeated coupons are not independent builds. Control limits describe observed variation; the customer LSL is a separate requirement. The parameter table's “usual range” is the observed range of unflagged build means, not a validated operating window or a causal recommendation.

## API examples

From a second PowerShell terminal while the app runs:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/profiles'
Invoke-RestMethod 'http://127.0.0.1:8000/datasets?process_type=waam'
Invoke-RestMethod 'http://127.0.0.1:8000/analyze?dataset=waam_stable_capable&lsl=895&process_type=waam'
Invoke-RestMethod 'http://127.0.0.1:8000/analyze?dataset=stable_capable&lsl=895'
curl.exe --fail --silent --show-error http://127.0.0.1:8000/analyze -F 'file=@tests/fixtures/spec_example.csv' -F 'lsl=980'
```

Use `curl.exe` explicitly because Windows PowerShell may alias `curl`. The known-answer upload returns 4 builds, 12 coupons, Cpk about 0.591, Ppk about 0.571, one failure, no flags and `not assessable` because fewer than 25 builds were supplied. See [app/README.md](app/README.md) for every route, parameter, response field and error.

## Verification

Run from the repository root after setup:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
npm.cmd --prefix app/frontend test
.\.venv\Scripts\python.exe demo/check.py --base-url http://127.0.0.1:8000
.\.venv\Scripts\python.exe data/generate.py --check
.\.venv\Scripts\python.exe data/generate_waam.py --check
.\.venv\Scripts\python.exe data/validate.py
.\.venv\Scripts\python.exe data/validate_waam.py
.\.venv\Scripts\python.exe data/generate_additional.py --check
.\.venv\Scripts\python.exe data/validate_additional.py
.\.venv\Scripts\python.exe data/generate_inspection.py --check
.\.venv\Scripts\python.exe data/validate_inspection.py
```

The scenario checker needs the running server; omit `--base-url` for core-only checks. It does not rewrite results unless `--output` is supplied. Frontend tests check rendering and request wiring using fixtures; the live checker compares all core fields using the integrated datasets.

Baseline local Windows verification before the WAAM increment: **30 Python tests and 5 subtests passed**, **6 frontend tests passed**, the frontend build succeeded, and all three live scenario/API comparisons passed. Python tests emitted a Starlette/httpx deprecation warning. The browser reported a missing favicon (404), without affecting analysis.

**Cross-platform reproducibility:** the earlier Windows byte-check failure came from CRLF checkout endings, not changed measurements. Text files now declare LF endings in `.gitattributes`, runtime data copies were resynced, and the bundle tool writes LF requirements explicitly. `data/validate.py` now passes reproducibility, schema, scenario and edge-case checks without weakening its byte comparison. Existing clones may need a clean checkout to adopt the attributes. Independent fresh-clone human reproduction remains pending.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Dashboard 404 | Build React before starting Python; restart after creating a missing `app/frontend/dist/`. |
| Empty dataset selector | Copy `data/*.csv` to `app/data/`, then refresh. |
| Port 8000 occupied | Reuse the running preview or stop the server you previously started before restarting. |
| Missing command/module | Check Node/npm PATH and use the `.venv` Python explicitly. |
| Upload rejected | Check the error, required columns, finite strength and equal coupon counts. |

## Deployment and project map

**Public Posit Connect URL:** [https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/](https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/) (H-06). Verified logged out on October 22, 2026: the address opens the dashboard, `/health` answers `{"status":"ok"}`, and LPBF `stable_capable` at LSL 895 shows capable, Cpk 1.683, Ppk 1.789, matching the core. The workflow now tests and deploys automatically on pushes to `main` that change `app/`, `data/` or the configured deployment paths; it can also be started manually. A push is a deployment action when publisher secrets are configured. Follow the [deployment handoff](.github/scripts/README.md). Keep credentials in environment settings or repository secrets. Do not invoke publishing scripts to preview the app.

| Location | Purpose |
| --- | --- |
| `app/qc.py` | Framework-independent statistics |
| `app/app.py`, `app/profiles/` | API, profile registry, LPBF and WAAM mappings |
| `app/frontend/` | React/Vite dashboard |
| `data/`, `demo/` | Synthetic CSVs, codebook, walkthrough and checker |
| `tests/` | Statistical, API and bundle API tests (including `test_bundle_api.py`) |
| `.github/` | Deployment validation and publishing tools |

Current scope excludes other methods, unequal subgroups, regression, ANOVA, FMEA, multi-defect event analysis, predictive models and numerical parameter-change recommendations. Signal and primary-inspection-defect Paretos, fixed-limit date views and evidence-based investigation checks are implemented. See [SPEC](SPEC.md), [decisions](docs/decisions.md), [task ledger](CONTRACT.yaml) and [rubric](docs/criteria.md). Starter provenance is documented in [demos](demos/README.md) and the deployment handoff; see the [MIT license](LICENSE).

## Submission evidence and remaining checks

For the complete current 100-point mapping, use [docs/evaluation.md](docs/evaluation.md).
[docs/remaining-work.md](docs/remaining-work.md) is the open-ended handoff; the table below is a
compact overview. The H-10 through H-14 verification paragraphs retain historical increment results.

| Rubric item | Evidence to review | Remaining action |
| --- | --- | --- |
| Effective working tool (25) | Local dashboard/API, upload workflow and sixteen examples (four per process) | Done: public URL above, verified logged out (H-06) |
| Valid QC analysis (25) | SPEC formulas; known-answer and degenerate tests in `tests/` | Retain actual passing output and explain assumptions |
| Prompt fit, user, minimal inputs (15) | SPEC use case; three required CSV columns plus customer LSL | Confirm the stated workflow with a quality-engineering reviewer |
| Clear demonstration (10) | Interactive 14-lesson HTML tutorial, written walkthrough and synthetic API captures in `demo/` | Independent teammate reproduction |
| Documentation (10) | This quick start and API/function reference | Independent fresh-clone walkthrough |
| Datasets and codebook (10) | Sixteen labeled synthetic files; units, seeds and collection sources | Verify reproducibility on the supported checkout |
| Public reproducible repository (5) | GitHub source, lockfile and run/test commands | Fresh-clone verification and final Devpost links |

Example known-answer evidence (LSL 980 MPa): X-bar center 1000 MPa; limits 980.456–1019.544 MPa; S center 10 MPa; upper limit 25.682 MPa; Cpk 0.591; Ppk 0.571; 1/12 failures; capability withheld for too few builds. Constant-data tests require undefined indices and a no-variation reason; one-build, unequal-count and missing-strength tests require rejection. These checks validate implementation against the stated examples, not hardware qualification.

The WAAM release manifest was generated locally with rsconnect-python 1.32.0 under Python 3.12.15. All 18 runtime checksums, isolated dashboard/assets/health, known-answer upload and six scenario comparisons passed. The user approved committing and pushing this WAAM release; the existing workflow publishes qualifying pushes to main. Confirm server interpreter support before publication. Public deployment and independent human checks remain pending; no scores are claimed here.

## WAAM sampling and compatibility

WAAM selection reuses the measured-strength X-bar/S engine; it does not estimate strength from arc settings. Use equal-size rational build subgroups, comparable testing and a customer-provided LSL. A process name does not establish that these assumptions hold. If the sampling design does not fit, do not interpret the capability assessment.

Legacy requests that omit `process_type` remain LPBF. `/profiles` describes supported measurements and units; `/datasets?process_type=waam` lists WAAM examples. GET analysis takes `process_type` as a query parameter and POST takes it as a multipart form field. Existing LPBF dataset IDs and core output keys remain unchanged. Full synthetic WAAM construction and its limitations are in the [codebook](data/README.md#waam-extension-h-10).

H-10 local verification: **37 Python tests**, **8 frontend tests**, both dataset validators and five bundle tests passed. All six scenarios were exercised in the browser and through the API, including process switching, stale context, uploads, mismatch errors, delayed catalogs and mobile/keyboard use. The core statistical function is unchanged. The WAAM source increment was committed/pushed before the later extensions; public deployment verification remains H-06, and independent reproduction remains open.


## Signal Pareto and investigation checks (H-11 to H-13)

The **Control-chart signal Pareto** ranks mean-below-LCL, mean-above-UCL and S-above-UCL occurrences using the existing chart rules. Bars show counts; the right-axis line shows cumulative percentage. A build can trigger two signals. These are not inspection defect categories, coupon failure rates or proven causes. With no signals, the dashboard explains why there is nothing to rank. Expand the data table for affected builds and exact percentages.

**Recommended investigation actions** show ordered checks with the triggering evidence: test-record review, instability investigation, baseline review, zero variation or insufficient samples, capability improvement, distribution checks and selected-process logs. Expand further checks and affected build IDs as needed. Guidance does not prescribe machine settings or replace engineering decisions. See the [workflow and response contract](docs/signal-investigation.md).

Select **Laser DED > Unstable process shift** to exercise all three signal categories: 16 signals on 15 builds; D024 has both a low-mean and high-S signal. Required CSV columns and original LPBF/WAAM numeric results are unchanged. The new methods each have three additional reproducible synthetic examples, with units and seeds in the codebook. No trained strength-prediction model is included.

This increment is a local review candidate; public deployment and independent teammate walkthrough remain pending. The normal launch command above uses port 8000; the current parallel review preview uses http://127.0.0.1:8001/dashboard/.

H-13 historical local verification: **54 Python tests plus 14 subtests**, **14 frontend tests** and production build, all three dataset validators, all twelve browser/API scenarios, and five bundle tests passed. The regenerated Python 3.12 manifest verified **28 runtime files**, and the isolated bundle served the dashboard/assets, known-answer upload and twelve scenarios. The engine and original six dataset bytes were unchanged.


## Expanded Pareto exploration (H-14)

Select **Inspection defect example** under any process to see both signal and inspection-defect Paretos. Click a bar or focus it and press Enter/Space to filter build details and investigation checks. Selected builds are outlined on the full strength charts; **Clear selection** restores flagged builds in the applied date window. Expand coupon records for original data-row numbers, measured strengths and inspection labels.

Use **From build date**, **Through build date** and **Apply date range** for an inclusive evidence window. Either bound may be blank. Displayed applied dates and counts remain visible while editing draft dates; **Reset Pareto view** restores the full window. The complete-file control limits, Cpk/Ppk, strength-failure totals and verdict remain unchanged. Invalid ranges preserve the last successful view and show a recovery message.

Charts show counts, category shares, cumulative labels and an **80% reference**. Signal percentages use signal occurrences; defect percentages use recorded defective coupons. Inspection coverage, explicit no-defect results and missing records are reported separately. The four new synthetic examples each have 39 primary defects, 45 explicit no-defect results and six unrecorded results; they preserve the original strength data. A physical inspection category is never inferred from a chart signal or a strength failure.

See [the complete interaction/API guide](docs/pareto-explorer.md) and [inspection codebook](data/README.md#synthetic-inspection-examples-h-14). All sixteen datasets have stable IDs. This remains a local review build; no commit, push or deployment is part of this change.

H-14 local verification: **75 Python tests plus 18 subtests**, **19 frontend tests** and production build, all four data validators/generator checks, all sixteen browser/API scenarios, five bundle tests and the isolated known-answer/dashboard checks pass. The final manifest verifies **34 runtime files**. Keyboard selection, mobile scrolling, native uploads, fixed-limit single-day views, invalid/empty ranges, clearing and reanalysis resets were exercised. The core and original source datasets remain unchanged; release review and independent human reproduction remain pending.

## Documentation and interactive training (H-15)

The [self-contained HTML walkthrough](demo/slidedeck/index.html) provides 14 lessons with all sixteen
scenarios, exact source CSV downloads, chart/Pareto exploration, captured LSL/date experiments and
knowledge checks. The [demo instructions](demo/README.md#interactive-html-walkthrough) explain offline
opening, HTTP preview, keyboard navigation, printing and rebuilding verified captures.

Current local checks: **78 Python tests plus 18 subtests**, **19 frontend tests/build**, four validators,
sixteen API parity cases and three tutorial artifact tests pass (the three are included in the 78).
Browser checks cover navigation, selections, source-byte download parity, offline file opening,
responsive layout and printing. The unchanged rubric has a complete [evidence mapping](docs/evaluation.md).
The [remaining-work list](docs/remaining-work.md) stays open-ended. H-06 and deployment files were
preserved; no commit, push or deployment was performed for this update.
