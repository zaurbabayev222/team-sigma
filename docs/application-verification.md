# AeroQual application verification and fixes

Audited branch: **main**, commit **ec46030a5f7a56ddd9b795cd823d5e947af98407**.
The fast-forward pull added the application-only priority instructions. Previous application work is
in `6b4bc03`; the intervening `ede65e7` did not change the application runtime.
This report covers the working React/FastAPI application, not public hosting.

## Ownership and scope

H-05 owns the frontend; its overlap with the necessary functional fixes was reported before edits.
H-17 records the user-authorized scope without changing any existing owners or task records. The
existing UI design is preserved. H-02 data, H-06 files, H-07 READMEs and H-08 ignore rules are unchanged.
Only core/API safeguards, frontend request handling, regression tests and this application handoff
are changed. The user approved committing and pushing this scope to main after verification; no direct
deployment has been performed.

There is no root PRODUCT.md in the audited checkout; SPEC.md and the implemented profile registry
govern the application. Historical pre-implementation assessments are not treated as current status.

## Confirmed defects and fixes

| Reproduced behavior before the fix | Correction | Regression evidence |
| --- | --- | --- |
| Blank build IDs or dates could return HTTP 200 and `capable` | Core rejects null/blank/whitespace subgroup identity and order | Six identity/order cases; direct core and API |
| Conflicting dates within a build and invalid calendar dates could produce a verdict | Core requires one order value per build; API validates every build's ISO calendar date using the existing date helper | Four-profile conflict cases, three malformed date cases; unfiltered/filtered consistency |
| `min_builds=0/1`, negative/zero/non-finite Cpk targets were accepted | Validate decision settings in the plain engine; valid custom settings remain supported | GET and multipart cases |
| Infinite optional process measurements caused JSON serialization HTTP 500 | Return a field- and data-row-specific HTTP 400 before publishing results | One optional parameter for each of four profiles |
| 400-coupon subgroups caused gamma overflow HTTP 500 | Evaluate the same c4 gamma ratio in log space only when the original calculation overflows | Large equal-subgroup HTTP regression; approved n=3 path unchanged |
| Non-JSON HTTP 503 responses surfaced a parsing exception | Request adapter reports HTTP status and retry guidance | Vitest and injected browser failure |
| Network failures and structured validation errors lacked useful context | Reachability guidance; field/message formatting for FastAPI errors | Vitest and browser recovery |
| A malformed HTTP 200 analysis could crash result rendering | Validate the display schema before accepting a response; reject absent/wrong process attribution | Malformed-response and process-attribution Vitest cases; browser error injection |
| Prior KPIs remained visible while a replacement analysis was pending | Clear the old analysis before requesting; process changes also clear results | Delayed failure check, server/schema/network errors and process-switch browser checks |

The date correction deliberately tightens the prior legacy behavior that deferred source-date validation
until a date filter was requested. That old expectation was updated in `tests/test_pareto_views.py`.
No default thresholds, chart rules, capability formulas or scenario data have changed.

## Profile/scenario verification matrix

Every cell below passed **real GET analysis, real multipart CSV upload, exact GET/upload response
parity and live React display checks** at illustrative LSL **895 MPa**. Each dataset has 30 builds ×
3 coupons. Failure counts are measured coupons, not builds.

| Implemented profile | Stable/capable | Stable/incapable | Unstable shift | Inspection sample |
| --- | --- | --- | --- | --- |
| LPBF (`lpbf`) | capable; 0/90 failures | not capable; 17/90 | withheld; 0/90 | withheld; 0/90 |
| WAAM (`waam`) | capable; 0/90 | not capable; 18/90 | withheld; 5/90 | withheld; 5/90 |
| EB-PBF (`ebpbf`) | capable; 0/90 | not capable; 16/90 | withheld; 4/90 | withheld; 4/90 |
| Powder-fed laser DED (`laser_ded`) | capable; 0/90 | not capable; 22/90 | withheld; 12/90 | withheld; 12/90 |

The registry contains exactly four profiles and sixteen datasets. LPBF's three original strength IDs
are unprefixed; inspection is `lpbf_inspection_demo`. Other IDs use their process prefix plus
`stable_capable`, `stable_incapable`, `unstable_shift` or `inspection_demo`.

All sixteen complete core result dictionaries were compared to the audited Git revision and are
**exactly unchanged**, including chart limits, per-build means/S, flags, capability, failure counts,
diagnostics and verdicts. Existing known-answer checks retain the project tolerances: Cpk/Ppk within
0.001 and the SPEC chart-limit examples within 0.01. The four validators independently check fixture
reproduction, schemas, planted conditions and inspection counts.

## Commands and observed results

Run from the repository root using the selected project's Python environment:

```powershell
python -m pytest tests/test_qc.py tests/test_api.py tests/test_bundle_api.py tests/test_process_profiles.py tests/test_additional_processes.py tests/test_investigation.py tests/test_signals.py tests/test_pareto_views.py tests/test_application_safeguards.py -q
npm.cmd --prefix app/frontend test
npm.cmd --prefix app/frontend run build
python data/validate.py
python data/validate_waam.py
python data/validate_additional.py
python data/validate_inspection.py
```

- Application-only pytest suite: **100 passed, 18 subtests passed**, one existing Starlette/httpx
  TestClient deprecation warning. This is not a claim that unrelated artifact suites were run.
- Frontend: **25 tests passed** (19 existing display/contract cases plus six request safeguards).
  Production Vite build passed; no lint/typecheck scripts are defined in this plain-JavaScript package.
- All four validators: **PASS**. No dataset generator or source CSV was modified.
- Configured Playwright MCP executed `tests/application_browser.js` against Vite on 5175 and FastAPI
  on 8002: **16 named + 16 uploaded cases passed**, with no JavaScript page errors.
- Additional browser checks: catalog outage, upload during outage, retry recovery, delayed catalog
  suppression, chart keyboard readouts, Pareto Enter selection, source coupon traceability, date reset,
  empty/invalid windows, full-log invariance, non-JSON 503, malformed success response and network failure.
- Responsive application checks: **375, 768 and 1440px**, no document-level horizontal overflow;
  local chart/table scrolling is intentional.
- Console inspection: expected HTTP/network errors from injected failures, plus a pre-existing missing
  favicon 404. No React exception was observed. A favicon change is not necessary for application safety.
- Read-only preservation check: **87 protected existing files unchanged**, including dataset and H-06
  assets. Existing contract task blocks are retained; only the H-17 entry is appended.

To repeat browser regression through the configured MCP, invoke `browser_run_code` with filename
`tests/application_browser.js` after starting the services below. It uses real repository CSV uploads;
run the MCP server from this repository so relative `data/` paths resolve. It returns the per-case matrix.

## Clean local source verification

A new, application-only source copy was created under ignored `.venv/h17-current-clean` with no existing
node_modules or dist. It contained the candidate fixes, not a published Git revision at verification time.
The already isolated Python 3.12 environment `.venv/h15-fresh-env` was reused because its pinned
dependencies match the unchanged requirements; `pip check` reported no broken requirements.
The clean-copy run printed its own `app/qc.py` path, proving it imported the clean source rather than
the working checkout. From that source directory, its application suite passed **100 tests + 18 subtests**.

`npm ci` installed the 100 locked frontend packages in the new copy. Its **25 frontend tests and build
passed**. Source CSVs were copied to its runtime `app/data/` using the documented startup step.
The fresh built dashboard started with FastAPI on port 8003, analyzed LPBF in the browser, and all
sixteen named API scenarios returned HTTP 200. This validates a clean source setup without claiming a
new public-clone test or an independent teammate review.

## Exact local preview in Positron / Windows PowerShell

The current updated development services are already running:

- React/Vite: **http://127.0.0.1:5175/**
- FastAPI health: **http://127.0.0.1:8002/health**
- Interactive API reference: **http://127.0.0.1:8002/docs**

To restart them manually, use separate integrated terminals at the repository root. Stop an existing
service before reusing its port. No execution-policy change or virtual-environment activation is needed.

Terminal 1, using the existing tested local Python 3.12 environment:

```powershell
.\.venv\release312\Scripts\python.exe -m uvicorn app.app:app --host 127.0.0.1 --port 8002
```

Terminal 2:

```powershell
$env:Path = 'C:\Program Files\nodejs;' + $env:Path
$env:VITE_API_URL = 'http://127.0.0.1:8002'
npm.cmd --prefix app/frontend run dev -- --host 127.0.0.1 --port 5175 --strictPort
```

The environment variable belongs in the terminal that launches Vite. Without it, the frontend's
relative production API path targets the Vite origin. No proxy or hosting configuration was changed.
If Node is already on PATH, the PATH line is optional. Use `Ctrl+C` in each terminal to stop it.

For a **new local setup**, first install Python 3.12 and Node/npm, then from the repository root:

```powershell
python -m venv .venv/local-app
.\.venv\local-app\Scripts\python.exe -m pip install -r app/requirements.txt
npm.cmd --prefix app/frontend ci --no-audit --no-fund
Copy-Item -Path data/*.csv -Destination app/data/
```

Use `.\.venv\local-app\Scripts\python.exe` in Terminal 1. Confirm `python --version` refers to the
intended interpreter before creating that environment. Network access is needed for uncached packages.
The dataset copy is required for built-in examples; forgetting it causes empty catalogs/404s.

For a single local production-build preview, first remove any temporary VITE_API_URL override if a
same-origin bundle is intended, then build and start Uvicorn:

```powershell
Remove-Item Env:VITE_API_URL -ErrorAction SilentlyContinue
npm.cmd --prefix app/frontend run build
.\.venv\release312\Scripts\python.exe -m uvicorn app.app:app --host 127.0.0.1 --port 8002
```

The built dashboard is then at `http://127.0.0.1:8002/dashboard/`. Vite serves at `/` on port 5175.

## Statistical boundaries and remaining risks

- No root cause, approved operating window or product-release authority is inferred. Parameter
  ranges describe unflagged-build observations. Normality diagnostics remain descriptive.
- Compatibility of alloy, orientation, heat treatment and test population still depends on truthful
  source selection; the minimal schema cannot infer unrecorded factors. Explicit process tags and
  known foreign-profile columns remain checked. No speculative new material/specification schema was added.
- Required coupon strengths must be finite. Optional blank/non-numeric context retains the existing
  unavailable-value behavior; explicit infinities now reject rather than causing a server failure.
- Core validation row labels are DataFrame indices; investigation coupon rows are one-based data rows
  excluding the header. Correct the indicated source record rather than treating missing data as a pass.
- Full-log limits include signaled builds; prospective monitoring still requires an engineering-justified
  stable baseline. Custom valid minimum-build and Cpk settings are supported; dashboard defaults remain 25/1.33.
- The existing deprecation warning and favicon 404 remain. No browser engines beyond configured Chromium,
  real customer datasets, independent teammate review or public environment were claimed as verified.
- The user approved committing and pushing these verified changes; no other task ownership was reassigned.
- H-06/release assets were intentionally not refreshed. Runtime-source changes will require a separate
  coordinated checksum/release review before any later publishing step that runs existing automation.

Context7 verified the official [Python lgamma definition](https://github.com/python/cpython/blob/main/Doc/library/math.rst)
for the overflow-only gamma-ratio evaluation and [FastAPI validation structure](https://fastapi.tiangolo.com/tutorial/query-params/)
for actionable field errors. The numerical estimator and default decision rules remain unchanged.
