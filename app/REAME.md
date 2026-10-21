# AeroQual Backend and Statistical Function Reference

This document explains the Python backend for **AeroQual**, the titanium additive manufacturing quality-monitoring prototype developed by Team Sigma Airlines. See the [main project README](../README.md) for the use case, input-data contract, demo status, and overall quick start.

> **Current scope:** This README documents the implemented Python engine (`qc.py`), LPBF profile (`profiles/lpbf.py`), FastAPI routes (`app.py`), and command scripts. React dashboard work and live deployment are separate tasks, tracked in `CONTRACT.yaml`.

## 1. Files and responsibilities

| File | Responsibility |
| --- | --- |
| `qc.py` | Framework-independent statistical calculations; no API or plotting code. |
| `app.py` | Input parsing, validation delegation, optional parameter summary, and HTTP endpoints. |
| `profiles/lpbf.py` | Process profile defining column names, display labels, units, and optional LPBF parameters. |
| `requirements.txt` | Python dependency versions. |
| `testme.sh` | Starts Uvicorn / FastAPI on port 8000. |
| `sync_data.sh` | Copies `../data/*.csv` into `app/data/` for built-in dataset lookup and deployment. |
| `manifestme.sh` | Generates Posit Connect manifest after syncing available datasets. |
| `deployme.sh` | Publishes backend to Posit Connect using appropriate credentials. |

The authoritative statistical calculations are performed in `qc.py`, not in FastAPI, React, or the LPBF profile.

## 2. Setup and start

From the **repository root** (including in GitHub Codespaces):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
bash app/testme.sh
```

Open http://127.0.0.1:8000/docs to inspect the interactive OpenAPI documentation. On Codespaces, use the forwarded port 8000 URL instead. `bash app/testme.sh` is the **one-command launch after dependencies have been installed**; it starts the API, not the unfinished React dashboard. Stop with `Ctrl+C`.

Run the test suite separately:

```bash
python -m pytest tests -q
```

## 3. Input schema and settings

Required CSV columns, one row per coupon:

| Column | Format | Meaning |
| --- | --- | --- |
| `build_id` | Text | Subgroup identifier. |
| `build_date` | `YYYY-MM-DD` | Build order (lexically sorted in the current engine). |
| `uts_mpa` | Finite numeric, MPa | Ultimate tensile strength. |

Optional LPBF process columns, used **only** for descriptive investigation: `chamber_oxygen_ppm` (ppm), `powder_reuse_count` (count), and `laser_power_w` (W).

Analysis parameters:

- **`lsl: float`**. Required, finite lower specification limit (MPa). Counts as a failure when `uts_mpa < lsl`; equality passes.
- **`min_builds: int = 25`**. Minimum number of distinct builds required for an assessable capability verdict.
- **`cpk_target: float = 1.33`**. Minimum lower-side Cpk for a `capable` verdict (not a universal aerospace certification criterion).

The statistical function requires two or more builds, at least two coupons per build, and the same subgroup size in every build. Missing required fields, blank or nonnumeric measurements, unequal subgroup sizes, or a non-finite LSL raise an error. The API returns HTTP 400 for detected dataset/statistical input errors and HTTP 404 for unknown bundled dataset names.

## 4. Statistical functions: `qc.py`

### `c4_constant(n)`

Returns the finite-subgroup-size bias-correction constant:

`c4 = sqrt(2/(n - 1)) * Gamma(n / 2) / Gamma((n - 1) / 2)`

Used to estimate short-term within-build standard deviation. `n` is the number of coupons per build; the analysis function ensures `n >= 2` before calling this helper.

### `chart_constants(n)`

Returns a dictionary with `c4`, `A3`, `B3`, and `B4` based on the subgroup size, rather than hard-coding factors for a specific sample size. For n = 3, factors are approximately `c4 = 0.8862`, `A3 = 1.954`, `B3 = 0`, and `B4 = 2.568`.

### `analyze(df, lsl, subgroup_col="subgroup", order_col="order"
value_col="value", min_builds=25, cpk_target=1.33)`

**Inputs:** A pandas DataFrame containing one measurement per row, a numeric LSL, column-name mappings, a minimum build count, and a Cpk target. The API supplies the LPBF mapping: `build_id`, `build_date`, `uts_mpa`.

**Sequence of operations:**

1. Validate required columns, finite strength measurements and LSL, number of builds, and equal subgroup sizes.
2. Group coupons by build and sort build groups using their recorded `order` field.
3. Calculate each build's mean and sample standard deviation `s` (`ddof=1`).
4. Calculate the grand mean `X-double-bar` and the mean within-build standard deviation `s-bar`.
5. Calculate X-bar limits: `grand_mean +/- A3 * s_bar`.
6. Calculate S-chart limits: `B3 * s_bar` to `B4 * s_bar`.
7. Flag builds whose means fall outside X-bar limits or whose `s` is above the S upper limit. The implementation does **not** implement additional run-pattern control-chart rules.
8. Estimate `sigma_short = s_bar / c4` and `sigma_total = sample standard deviation of all coupons`.
9. Calculate lower-side `Cpk = (grand_mean - lsl) / (3 * sigma_short)` and `Ppk = (grand_mean - lsl) / (3 * sigma_total)`. Undefined capability values are represented by JSON `null`, not infinity.
10. Count coupon failures strictly below LSL and compute their fraction. Also report a Shapiro-Wilk normality p-value when possible.
11. Produce a verdict and explanatory reason according to the checks below.

**Verdict priority:**

| Condition (evaluated in order) | `verdict` |
| --- | --- |
| No variation means Cpk or Ppk cannot be computed | `not assessable` |
| One or more flagged builds | `not assessable` |
| Fewer builds than `min_builds` | `not assessable` |
| Otherwise `cpk >= cpk_target` | `capable` |
| Otherwise | `not capable` |

The function may still return numerical Cpk/Ppk when stability or sample-count checks fail, but those numbers must **not** be treated as validated capability. The statistical engine provides a summary, not an automated hardware-release decision.

**Response dictionary fields:**

| Key | Type | Meaning |
| --- | --- | --- |
| `n_builds` | Integer | Distinct builds. |
| `n_per_build` | Integer | Coupons per build. |
| `builds` | List of objects | Each has `build_id`, `order`, `mean`, `s`, `flagged`, `reason`. |
| `xbar` | Object | `center`, `lcl`, `ucl` of build-mean chart. |
| `s_chart` | Object | `center`, `lcl`, `ucl` of within-build variation chart. |
| `sigma_short` | Number | Estimated short-term/within-build standard deviation. |
| `sigma_total` | Number | Sample standard deviation over all coupons. |
| `cpk`, `ppk` | Number or null | Lower-side capability/performance indices. |
| `n_coupons`, `n_failures` | Integers | Tested coupons and those below LSL. |
| `failure_rate` | Number from 0 to 1 | Observed proportion below LSL. |
| `shapiro_p` | Number or null | Shapiro-Wilk diagnostic p-value when computable. |
| `verdict` | String | `capable`, `not capable`, or `not assessable`. |
| `reason` | String | Human-readable basis for verdict. |

The API layer adds `profile` and `parameters` to this result.

## 5. API orchestration functions: `app.py`

### `parameter_summary(df, result)`

Reads any LPBF optional process columns present in the input CSV and returns:

- `columns`: optional column names that were provided;
- `usual_range`: observed min/max of **per-build averages for unflagged builds**, for each optional column with data;
- `flagged_builds`: flagged build IDs with their optional-parameter values, computed as per-build averages.

These comparisons are descriptive. They cannot establish that oxygen, powder reuse, or laser power **caused** a shift. Missing optional measurements can appear as `null`; optional parameters are not fed into capability calculations.

### `run_analysis(df, lsl, min_builds, cpk_target)`

Checks the three mandatory LPBF columns, calls `qc.analyze(...)` with the profile's column mapping, and appends process `profile` metadata and the optional `parameters` summary. A `ValueError` from core QC input validation becomes HTTP 400 with an explanatory error message.

## 6. HTTP endpoint reference

The application exposes these routes through FastAPI:

| Method | Endpoint | Request | Response |
| --- | --- | --- | --- |
| `GET` | `/` | None | A service-running message and `/docs` pointer. |
| `GET` | `/health` | None | `{ "status": "ok" }`. |
| `GET` | `/datasets` | None | `{ "datasets": ["name", ...] }` from `app/data/*.csv`. |
| `GET` | `/analyze` | Query `dataset` (without `.csv`), `lsl`; optional `min_builds`, `cpk_target` | Full analysis JSON or 404/400. |
| `POST` | `/analyze` | Multipart form-data `file` (CSV), `lsl`; optional `min_builds`, `cpk_target` | Full analysis JSON or validation error. |
| `GET` | `/__docs__/` | None | Redirect to `/docs`. |
| `GET` | `/docs` | None | FastAPI-generated interactive API documentation. |

### Upload a CSV

From a *second terminal*, with the backend running:

```bash
curl -sS -X POST http://127.0.0.1:8000/analyze \
  -F 'file=@/path/to/builds.csv;type=text/csv' \
  -F 'lsl=980' \
  -F 'min_builds=25' \
  -F 'cpk_target=1.33'
```

Replace `/path/to/builds.csv` with a real file. To create a known-answer file and see the expected results, follow section 5 of the [main README](../README.md).

### Analyze a bundled dataset

When H-02 supplies `data/*.csv`, first run from the repo root:

```bash
bash app/sync_data.sh
```

Then, with the backend running, list datasets and analyze one of the names returned:

```bash
curl -sS http://127.0.0.1:8000/datasets
curl -sS 'http://127.0.0.1:8000/analyze?dataset=stable_capable&lsl=980'
```

The `stable_capable` request is an **example name**, not a claim that the corresponding file is currently available. The server returns 404 if that dataset has not been created and copied to `app/data/`. The backend only accepts letters, digits, underscores, and hyphens in dataset names.

## 7. Known-answer checks and tests

In `SPEC.md`, section 4, the four-build, three-coupon, LSL = 980 MPa example has:

- X-bar center: `1000` MPa, control limits approximately `980.46` to `1019.54` MPa.
- S center: `10` MPa, control limits approximately `0` to `25.68` MPa.
- Lower-side Cpk approximately `0.591`, lower-side Ppk approximately `0.571`.
- Failure rate `1/12` = `8.3%`.
- Verdict: `not assessable`, because 4 builds are fewer than the default 25 even with no flagged build.

Run the repository's existing tests after installing dependencies:

```bash
python -m pytest tests -q
```

The task ledger records previously passing statistical and API test runs; these should be repeated on the current branch before declaring reproducibility.

## 8. Error handling and limitations

**Typical error conditions:** missing `build_id`, `build_date`, or `uts_mpa`; blank/non-numeric/infinite strengths; an invalid LSL; a single build; unequal subgroup sizes; fewer than two measurements in a subgroup; a missing built-in dataset; or an unreadable upload.

**Statistical limitations:** X-bar/S monitoring assumes natural equal-sized build subgroups, stable measurement conditions, and sufficiently appropriate distributional assumptions. Shapiro-Wilk is a diagnostic, not a universal validity test. An unflagged chart is not proof of no risk, and a Cpk verdict is not a qualification decision. Current optional-parameter comparisons are not a causal model.

**Functional limitations:** Only the LPBF profile is implemented. The React UI, synthetic multi-scenario dataset suite, full demo walkthrough, and public Posit Connect URL remain dependent on H-02/H-05/H-06. No authentication or database is provided in the MVP; do not upload proprietary production measurements to an unsecured public instance.

## 9. Deployment handoff

H-06 owns Posit Connect deployment. Existing scripts are:

```bash
bash app/sync_data.sh     # copy CSVs into the app bundle
bash app/manifestme.sh    # install rsconnect-python and generate manifest.json
bash app/deployme.sh      # deploy using configured account or environment variables
```

These scripts require appropriate permissions and deployment configuration. Never commit `CONNECT_API_KEY` or `.env` credentials. After the deployment owner confirms the public URL and tests it from a logged-out browser, update the main README's **Live deployment** section.

**References:** [Project README](../README.md) · [SPEC](../SPEC.md) · [Task ledger](../CONTRACT.yaml) · [Project overview](../PROJECT_OVERVIEW.md).
