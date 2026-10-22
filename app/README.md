# AeroQual function and API reference

Start with the [root README](../README.md) for Windows PowerShell setup, dashboard usage, observed verification results and current limitations. The [codebook](../data/README.md) defines the synthetic datasets; the [walkthrough](../demo/README.md) explains their outputs.

## Launch and frontend integration

After installing requirements, copying CSVs to `app/data/` and building React, run from the **repository root**:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/dashboard/`. The root stays API JSON. The dashboard mount is registered only if `frontend/dist/` exists when the application imports; build before starting and restart after creating a missing build.

In Bash with the intended Python environment active, `bash app/testme.sh` syncs data, installs/builds React and runs `app:app` from inside `app/`. This flat entrypoint also matches the deployment bundle; use `app.app:app` from the repository root.

React requests API routes one directory above `/dashboard/` by default. Separate Vite development requires an explicit API base:

```powershell
$env:VITE_API_URL = 'http://127.0.0.1:8000'
npm.cmd --prefix app/frontend run dev
```

Keep the backend running separately and open Vite's printed URL. Remove the override with `Remove-Item Env:VITE_API_URL` before building a portable same-origin release. Vite embeds these values at build time. The same-origin built dashboard is the locally verified preview path. React formats results and computes chart coordinates; Python calculates QC values.

## HTTP endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | `{"message":"AeroQual API is running!","docs":"/docs"}` |
| GET | `/health` | `{"status":"ok"}` |
| GET | `/datasets` | `{"datasets":["stable_capable","stable_incapable","unstable_shift"]}` after CSV synchronization |
| GET | `/analyze` | Analyze bundled CSV using query parameters |
| POST | `/analyze` | Analyze uploaded CSV using multipart fields |
| GET | `/docs`, `/openapi.json` | Interactive documentation and machine-readable schema |
| GET | `/__docs__/` | Redirect to `/docs` |
| GET | `/dashboard/` | Built dashboard, when present |

### Analysis parameters

| Name | Type | Default | Meaning |
| --- | --- | --- | --- |
| `dataset` | String | Required for GET | Filename without `.csv` from `app/data/`; letters, digits, underscore or hyphen only |
| `file` | CSV file | Required for POST | Multipart upload, one row per coupon |
| `lsl` | Float | Required | Customer lower strength limit, MPa |
| `min_builds` | Integer | 25 | Minimum builds for a capability verdict |
| `cpk_target` | Float | 1.33 | Lower-side Cpk target |

GET takes settings as query parameters. POST takes **multipart/form-data**, not JSON: file and scalar settings belong in the same form. This matches FastAPI's [File/Form documentation](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/), checked through Context7. The dashboard exposes LSL and dataset/upload selection; it uses defaults for the other settings.

PowerShell examples, from the root with the server running:

```powershell
$result = Invoke-RestMethod 'http://127.0.0.1:8000/analyze?dataset=stable_capable&lsl=895&min_builds=25&cpk_target=1.33'
$result | Select-Object verdict, cpk, ppk, n_failures, n_coupons
curl.exe --fail --silent --show-error http://127.0.0.1:8000/analyze -F 'file=@tests/fixtures/spec_example.csv' -F 'lsl=980' -F 'min_builds=25' -F 'cpk_target=1.33'
```

The known-answer upload returns Cpk `0.5908179503`, Ppk `0.5708992257`, failure fraction `1/12`, no flags and `not assessable` (four builds). X-bar limits are approximately 980.456 to 1019.544 MPa; S limits are 0 to 25.682 MPa. This validates arithmetic, not a material standard.

### Response fields

| Field | Shape / units | Meaning |
| --- | --- | --- |
| `n_builds`, `n_per_build`, `n_coupons` | Integers | Builds, equal coupons per build, total coupons |
| `builds` | List | Each has `build_id`, `order`, `mean`, `s`, `flagged`, `reason`; strength summaries in MPa |
| `xbar`, `s_chart` | `{center, lcl, ucl}` | Centers and control limits, MPa |
| `sigma_short`, `sigma_total` | Numbers, MPa | Within-build estimate and overall sample SD |
| `cpk`, `ppk` | Numbers or null | Dimensionless lower-side indices; null when the respective variation estimate is zero |
| `n_failures`, `failure_rate` | Integer; fraction 0–1 | Coupon count strictly below LSL and its fraction |
| `shapiro_p` | Number or null | Pooled normality diagnostic; null for zero overall variation |
| `verdict`, `reason` | Strings | Assessment and explanation |
| `profile` | Object | `name`, `label`, `value_label`, `value_unit` |
| `parameters` | Object | `columns`, `usual_range`, `flagged_builds` |
| `histogram` | List | `{lower, upper, count}` bins from NumPy automatic binning; edges in MPa |

`parameters.usual_range[column]` is `{min, max}` over build means of **unflagged builds**. `parameters.flagged_builds` contains `{build_id, values: {column: value}}`. Nonnumeric optional entries become missing; unavailable flagged values become null. A range is omitted if no usable unflagged values exist. Without recognized optional columns the object is `{"columns":[],"usual_range":{},"flagged_builds":[]}`. These observed ranges are not approved operating windows.

### Errors and caller responsibilities

| Status | Examples |
| --- | --- |
| 400 | Unreadable upload; missing required column; blank/non-numeric/nonfinite strength; fewer than two builds; unequal or fewer than two coupons per build; invalid finite LSL |
| 404 | Unknown or disallowed dataset ID, including names with `.csv` |
| 422 | Missing required request fields or framework-level numeric conversion failure |

Application errors normally return `{"detail":"message"}`; framework validation can return a detail list. Strength errors identify the DataFrame index, zero-based for ordinary CSV input, e.g. `blank or non-numeric 'uts_mpa' at row 5`.

Required LPBF CSV columns are `build_id`, `build_date`, `uts_mpa`. Optional columns are `chamber_oxygen_ppm`, `powder_reuse_count`, `laser_power_w`; see the [root input table](../README.md#inputs-and-parameters) for units. Provide nonblank IDs, consistent ISO dates, correct units, finite optional measurements and sensible positive settings. These are not all enforced: the engine stringifies IDs/dates, uses the first date per build, sorts lexically and does not validate calendar dates, conflicting dates, missing IDs or setting domain bounds. Optional parameter conversion is permissive. Large subgroup sizes may exceed the direct gamma calculation's numerical range; supplied datasets use three coupons per build.

## Python interface

```python
import pandas as pd
from app.qc import analyze

frame = pd.read_csv("data/stable_capable.csv")
result = analyze(
    frame, 895.0,
    subgroup_col="build_id", order_col="build_date", value_col="uts_mpa",
    min_builds=25, cpk_target=1.33,
)
print(result["verdict"], result["cpk"])
# capable 1.683472027406637
```

Run from the repository root. The signature is:

```python
analyze(df, lsl, subgroup_col="subgroup", order_col="order", value_col="value",
        min_builds=25, cpk_target=1.33)
```

`df` is a pandas DataFrame; `lsl` must be a finite Python integer/float, not boolean. Column arguments map subgroup, order and measurement. Direct callers using supplied CSVs must pass the LPBF mappings above because defaults are generic. The frame is not modified. Returns the core response fields above, without `profile`, `parameters` or `histogram`; bad core input raises `ValueError`.

### Calculations

Each build uses sample SD (`ddof=1`). `grand_mean` is the average build mean and `s_bar` the average build SD. For equal subgroup size `n`:

```text
c4 = sqrt(2/(n-1)) * Gamma(n/2) / Gamma((n-1)/2)
A3 = 3 / (c4 * sqrt(n))
B3 = max(0, 1 - 3*sqrt(1-c4^2)/c4)
B4 = 1 + 3*sqrt(1-c4^2)/c4
X-bar limits = grand_mean +/- A3*s_bar
S limits = B3*s_bar to B4*s_bar
sigma_short = s_bar/c4
sigma_total = sample SD of all coupons (ddof=1)
cpk = (grand_mean - lsl)/(3*sigma_short)
ppk = (grand_mean - lsl)/(3*sigma_total)
failure_rate = count(value < lsl)/n_coupons
```

`c4_constant(n)` returns c4; `chart_constants(n)` returns `{c4, A3, B3, B4}`. Both expect valid subgroup size `n >= 2` and are not standalone validators or API routes.

Flags use strict inequalities: mean below/above X-bar limits or SD above S UCL. S LCL is returned but not used for flags. Limits use the entire log, not a separate baseline. Verdict checks, in order:

1. Either index undefined: `not assessable`, no variation.
2. Any flagged build: `not assessable`, unstable.
3. Fewer than `min_builds`: `not assessable`, too few builds.
4. Cpk at/above target: `capable`; otherwise `not capable`.

Shapiro-Wilk uses pooled coupon values when total variation is positive; it does not gate the verdict. Approximate normality, rational subgroups, comparable tests and a suitable measurement system remain interpretation assumptions. The indices are lower-sided (Cpl/Ppl terminology), not two-sided. Missing strength causes rejection; failure rate describes tested coupons only, with no missing-test coverage model.

### API adapter and profile

`run_analysis(df, lsl, min_builds, cpk_target)` in `app.py` checks profile columns, calls `analyze`, converts its `ValueError` to HTTP 400 and adds profile, parameters and histogram. `parameter_summary(df, result)` describes optional parameters at build level. The API imports only `profiles/lpbf.py`; adding another profile file alone does not create process selection or change the active profile.

## Scripts and release boundaries

| File | Purpose |
| --- | --- |
| `testme.sh` | Bash: sync CSVs, install/build frontend, start API |
| `sync_data.sh` | Copy root `data/*.csv` into runtime `app/data/` |
| `manifestme.sh` | Build frontend and generate a local manifest using the shared bundle tool |
| `deployme.sh` | Prepare the bundle and publish from your own machine (the push-to-deploy workflow does this too); requires Bash 4+ |
| `requirements.txt` | Pinned direct Python application/test dependencies |

Every push to `main` that changes `app/`, `data/` or `.github/` tests and redeploys the app; see the [deployment handoff](../.github/scripts/README.md). The manifest targets Python 3.12 and checksums runtime files: after a source, data, dependency or dashboard change, re-write it with `bash app/manifestme.sh` and commit it with the change. Use `testme.sh`, not the publishing scripts, for local preview. Public deployment is unverified.

Run the commands in the [root verification section](../README.md#verification) for Python/frontend tests and live API parity. It records actual outputs and pending independent human reproduction. Local tests do not establish public deployment.
