# AeroQual

Titanium additive manufacturing quality dashboard by **Sigma Airlines**, Cornell SYSEN 5300 Six Sigma Hackathon, Virtual DL Challenge.

AeroQual helps a quality engineer review tensile-test coupons after each build: detect changes in process stability, assess lower-side strength capability, count observed failures, and inspect recorded conditions for flagged builds. The current release uses a **laser powder bed fusion (LPBF)** profile, React/Vite dashboard and FastAPI backend. Python calculates every QC result.

**Status:** the dashboard, API and three synthetic datasets work locally. Public Posit Connect deployment and independent fresh-clone teammate reproduction remain unverified. This prototype does not certify hardware or authorize release. All demonstration data and example limits are synthetic or illustrative.

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

1. Select **Stable and capable**, **Stable but not capable**, or **Unstable process shift**, or upload your coupon CSV. An upload takes precedence; use **Clear upload** to return to examples.
2. Enter **Minimum strength, LSL (MPa)** from the customer specification. The demo default **895 MPa** is illustrative, not a titanium acceptance standard.
3. Click **Analyze builds**. Review the labeled dataset/file and LSL, then read the separate stability, capability and observed-failure summaries. Expand the full backend reason when needed.
4. Inspect X-bar/S charts and the combined **Build investigation** table. Hover or keyboard-focus a chart point; **View all build data** exposes every plotted value. Expand diagnostics, observed reference ranges or distribution bins for supporting detail.
5. If you change an input, the page labels the previous results and asks you to analyze again. Inputs lock while a request is running; failed analyses display an error with recovery guidance.

The dashboard uses defaults of 25 builds and Cpk target 1.33. These settings are configurable through the API, not dashboard controls. Red squares identify builds flagged by either chart; circles represent unflagged builds. The table explains each flag. Chart and table containers scroll horizontally on small screens.

## Inputs and parameters

The CSV has one row per tested coupon. Keep comparable test conditions and one consistent ISO date per build.

| CSV column | Required | Units / format | Source |
| --- | --- | --- | --- |
| `build_id` | Yes | Text, shared by coupons in the build | Build traveler |
| `build_date` | Yes | `YYYY-MM-DD` | Build log |
| `uts_mpa` | Yes | Finite numeric MPa | Tensile-test report |
| `chamber_oxygen_ppm` | No | Numeric ppm | Printer log |
| `powder_reuse_count` | No | Nonnegative integer count | Powder record |
| `laser_power_w` | No | Numeric W | Printer settings |

At least two builds and two coupons per build are required, with equal coupon counts across builds. Blank, nonnumeric or infinite strength values cause an error, never a pass. Optional parameters are descriptive and do not affect capability. Extra columns are not analyzed.

| Separate parameter | Required | Default | Meaning |
| --- | --- | --- | --- |
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

Stability alone does not establish capability; zero observed failures alone does not establish capability. In the unstable example, strength and oxygen changes are planted together from B020. Their association is synthetic, not validated manufacturing physics.

The [complete walkthrough](demo/README.md) provides a three-minute judging sequence, local desktop/mobile captures, exact chart limits, flags, parameters and interpretation. Its Windows commands use the same environment as this README.

## Interpret the statistics

Each build is a subgroup. X-bar monitors build means; S monitors within-build sample SD. Limits are estimated from the **whole submitted file**, without a separately approved baseline. A mean outside X-bar limits or S above its upper limit flags a build. Lower S-limit violations and run/trend rules are not implemented.

Lower-side `cpk` uses within-build sigma estimated as average build SD divided by c4. Lower-side `ppk` uses overall coupon sample SD. These correspond to Cpl/Ppl terminology; the existing interface retains Cpk/Ppk labels. There is no fabricated upper strength limit. Failure rate counts coupons strictly below LSL; equality passes.

Verdict precedence is **not assessable** for undefined variation, then any flagged build, then too few builds; otherwise **capable** when Cpk meets the target, or **not capable**. Numeric indices may still appear for unstable data and are not an approval.

Interpretation assumes meaningful build subgroups, comparable approximately normal strengths and a suitable measurement system. The pooled Shapiro-Wilk p-value is diagnostic only: it does not prove normality or gate the verdict. Repeated coupons are not independent builds. Control limits describe observed variation; the customer LSL is a separate requirement. The parameter table's “usual range” is the observed range of unflagged build means, not a validated operating window or a causal recommendation.

## API examples

From a second PowerShell terminal while the app runs:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/datasets'
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
.\.venv\Scripts\python.exe data/validate.py
```

The scenario checker needs the running server; omit `--base-url` for core-only checks. It does not rewrite results unless `--output` is supplied. Frontend tests check rendering and request wiring using fixtures; the live checker compares all core fields using the integrated datasets.

Local Windows verification on October 21, 2026: **30 Python tests and 5 subtests passed**, **6 frontend tests passed**, the frontend build succeeded, and all three live scenario/API comparisons passed. Python tests emitted a Starlette/httpx deprecation warning. The browser reported a missing favicon (404), without affecting analysis.

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

**Public Posit Connect URL: not yet verified (H-06).** Local preview is not evidence of public deployment. The upstream workflow now tests and deploys automatically on pushes to `main` that change `app/`, `data/` or the configured deployment paths; it can also be started manually. A push is a deployment action when publisher secrets are configured. Follow the [deployment handoff](.github/scripts/README.md). Keep credentials in environment settings or repository secrets. Do not invoke publishing scripts to preview the app.

| Location | Purpose |
| --- | --- |
| `app/qc.py` | Framework-independent statistics |
| `app/app.py`, `app/profiles/lpbf.py` | API and LPBF mapping |
| `app/frontend/` | React/Vite dashboard |
| `data/`, `demo/` | Synthetic CSVs, codebook, walkthrough and checker |
| `tests/` | Statistical, API and bundle API tests (including `test_bundle_api.py`) |
| `.github/` | Deployment validation and publishing tools |

Current scope excludes other selectable printing processes, unequal subgroups, regression, ANOVA, FMEA, Pareto analysis, predictive models and automated parameter recommendations. See [SPEC](SPEC.md), [decisions](docs/decisions.md), [task ledger](CONTRACT.yaml) and [rubric](docs/criteria.md). Starter provenance is documented in [demos](demos/README.md) and the deployment handoff; see the [MIT license](LICENSE).

## Submission evidence and remaining checks

| Rubric item | Evidence to review | Remaining action |
| --- | --- | --- |
| Effective working tool (25) | Local dashboard/API, upload workflow and three examples | Publish and verify a public course Connect URL |
| Valid QC analysis (25) | SPEC formulas; known-answer and degenerate tests in `tests/` | Retain actual passing output and explain assumptions |
| Prompt fit, user, minimal inputs (15) | SPEC use case; three required CSV columns plus customer LSL | Confirm the stated workflow with a quality-engineering reviewer |
| Clear demonstration (10) | Three-minute walkthrough and real local captures in `demo/` | Independent teammate reproduction |
| Documentation (10) | This quick start and API/function reference | Independent fresh-clone walkthrough |
| Datasets and codebook (10) | Three labeled synthetic files; units, seeds and collection sources | Verify reproducibility on the supported checkout |
| Public reproducible repository (5) | GitHub source, lockfile and run/test commands | Fresh-clone verification and final Devpost links |

Example known-answer evidence (LSL 980 MPa): X-bar center 1000 MPa; limits 980.456?1019.544 MPa; S center 10 MPa; upper limit 25.682 MPa; Cpk 0.591; Ppk 0.571; 1/12 failures; capability withheld for too few builds. Constant-data tests require undefined indices and a no-variation reason; one-build, unequal-count and missing-strength tests require rejection. These checks validate implementation against the stated examples, not hardware qualification.

The release manifest was regenerated locally with rsconnect-python 1.32.0 under Python 3.12.15. All 14 runtime checksums and isolated bundle dashboard/assets, health, known-answer upload and three scenario comparisons passed. The candidate is prepared for review and release confirmation. Confirm server interpreter support before publication. Public deployment and independent human checks remain pending; no scores are claimed here.
