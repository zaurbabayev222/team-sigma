![](docs/images/banner_thin.png)

# 🎯 Cornell Six Sigma Hackathon

*Tackle real-world quality control problems drawn from industrial engineering,
healthcare systems, and energy systems!*

---

# AeroQual

### Titanium Additive Manufacturing Quality Dashboard

**Team:** Sigma Airlines  
**Event:** Cornell SYSEN 5300 Six Sigma Hackathon, Virtual DL Challenge (2026)  
**Challenge:** Prompt 1, *Industrial Systems: 3D Printing for Aerospace*  
**Repository:** https://github.com/zaurbabayev222/team-sigma

> **Development status (October 21, 2026):** The Python statistical engine and FastAPI backend are implemented. The synthetic datasets/codebook (H-02), React dashboard and dataset walkthrough (H-05), and public Posit Connect deployment (H-06) are not yet marked complete in `CONTRACT.yaml`. This README documents working source-code interfaces, planned deliverables, and the remaining verification steps separately. Do not treat planned features as deployed features.

## 1. What is AeroQual?

AeroQual is a quality-monitoring prototype for aerospace contractors that 3D-print titanium brackets. It helps a **quality engineer** interpret tensile-test results after each build and answer three questions:

1. **Is the printing process stable?** X-bar and S control-chart calculations flag unusual changes in strength averages or within-build variation.
2. **Can the process meet the customer's minimum strength?** Lower-side Cpk and Ppk summarize capability and overall process performance relative to a user-entered lower specification limit (LSL).
3. **How many tested coupons fail?** The tool reports the number and proportion of tensile-strength measurements below the LSL, with recorded process conditions to help investigate flagged builds.

The initial process profile is **laser powder bed fusion (LPBF)**. Statistical calculations in `app/qc.py` are independent of the printing technology; the LPBF-specific column mapping and optional process settings live in `app/profiles/lpbf.py`.

**Intended use:** Support engineering investigation and process improvement. This prototype does **not** certify aerospace hardware, approve product release, or establish an industry-wide material acceptance limit. All numerical examples and planned demonstration datasets are synthetic or illustrative.

## 2. Features and implementation status

| Component | What it provides | Status in task ledger |
| --- | --- | --- |
| Python statistics (`app/qc.py`) | X-bar/S limits, flagged builds, lower-side Cpk/Ppk, failure rate, normality p-value, verdict | H-03: done |
| FastAPI (`app/app.py`) | CSV upload, built-in dataset lookup, analysis JSON, API documentation | H-04: done |
| Sample datasets (`data/`) | Stable-capable, stable-incapable, unstable-shift scenarios and data dictionary | H-02: pending |
| React dashboard (`app/frontend/`) and walkthrough (`demo/`) | Visualization and interpretation of test scenarios | H-05: pending |
| Posit Connect | Public deployment | H-06: pending |

An API response includes the numerical chart series and limits even if the React charting page is not yet available.

## 3. Inputs

The API accepts a **CSV with one row per tensile-test coupon**, plus a customer-defined LSL in MPa.

| Field | Required? | Data type / unit | Description |
| --- | --- | --- | --- |
| `build_id` | Yes | Text | Identifies the printing build/subgroup. |
| `build_date` | Yes | `YYYY-MM-DD` | Orders builds chronologically for control-chart output. |
| `uts_mpa` | Yes | Numeric, MPa | Ultimate tensile strength from the coupon's tensile test. |
| `chamber_oxygen_ppm` | No | Numeric, ppm | Chamber oxygen recorded in the printer log. |
| `powder_reuse_count` | No | Numeric count | Number of powder reuses. |
| `laser_power_w` | No | Numeric, W | Laser power setting. |

Parameters supplied **separately from the CSV**:

| Parameter | Required? | Default | Interpretation |
| --- | --- | --- | --- |
| `lsl` | Yes | None | Lower specification limit, in MPa, supplied by the customer. |
| `min_builds` | No | `25` | Minimum number of builds before a capability verdict is assessable. |
| `cpk_target` | No | `1.33` | User-adjustable minimum acceptable lower-side Cpk. It is **not** a universal aerospace standard. |

**Input rules:** The current engine requires at least two builds and at least two coupons per build, with the **same number of coupons in each build**. The planned demonstrations use three coupons per build. `uts_mpa` must be present, numeric, and finite on every row; a missing or invalid measurement produces an error rather than a pass. Keep the same date for rows belonging to the same build and use ISO dates for predictable sorting. A measurement **equal to the LSL passes**; only measurements strictly below the LSL count as failures.

Example CSV structure (illustrative only):

```csv
build_id,build_date,uts_mpa,chamber_oxygen_ppm,powder_reuse_count,laser_power_w
B01,2026-10-01,990,120,1,200
B01,2026-10-01,1000,120,1,200
B01,2026-10-01,1010,120,1,200
B02,2026-10-02,1005,118,1,200
B02,2026-10-02,1010,118,1,200
B02,2026-10-02,1015,118,1,200
```

This is a minimal, two-build input example. It can be analyzed with a user-specified `lsl`, but its capability verdict will be `not assessable` under the default 25-build minimum. It is **not** the promised H-02 dataset collection.

## 4. Run locally or in GitHub Codespaces

Use a terminal in the **repository root**. The steps below also work inside the browser-based GitHub Codespaces editor, without installing Git locally on your Mac.

**Prerequisites:** Python 3 with a version compatible with the pinned `app/requirements.txt` dependencies, `pip`, and a Bash-compatible shell. Internet access is required when installing dependencies for the first time.

### First-time setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
```

### Start the backend (one command after setup)

```bash
bash app/testme.sh
```

The script starts Uvicorn and exposes the FastAPI app on **port 8000**. In Codespaces, select the forwarded port 8000 to open the API in a browser. Locally, visit:

- API health: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Dataset catalog: http://127.0.0.1:8000/datasets

Stop the server with `Ctrl+C`. No `git pull` is required to run an already-open Codespace; use `git pull` when you want to retrieve changes from the shared repository.

**Important:** `/datasets` currently returns an empty list if `app/data/` does not contain CSV files. When H-02 datasets are added under `data/`, copy them to the application's deployable data folder with `bash app/sync_data.sh` before using the built-in dataset endpoint.

## 5. Run a known-answer analysis

The repository's `SPEC.md`, section 4, provides a four-build example with 12 coupons and a lower specification limit of **980 MPa**. You can run the following commands in a *second terminal* while the API server is running. This creates a temporary CSV outside the repository so it does not modify the team's H-02 deliverables.

```bash
cat > /tmp/aeroqual-known-answer.csv <<'CSV'
build_id,build_date,uts_mpa
B1,2026-10-01,990
B1,2026-10-01,1000
B1,2026-10-01,1010
B2,2026-10-02,1005
B2,2026-10-02,1010
B2,2026-10-02,1015
B3,2026-10-03,975
B3,2026-10-03,990
B3,2026-10-03,1005
B4,2026-10-04,990
B4,2026-10-04,1000
B4,2026-10-04,1010
CSV

curl -sS -X POST http://127.0.0.1:8000/analyze \
  -F 'file=@/tmp/aeroqual-known-answer.csv;type=text/csv' \
  -F 'lsl=980'
```

**Expected checks** (rounded, from the approved known-answer example):

| Result | Expected value |
| --- | --- |
| Number of builds and coupons | 4 builds, 12 coupons |
| X-bar grand mean | 1000 MPa |
| Average within-build standard deviation | 10 MPa |
| X-bar lower / upper limits | 980.46 / 1019.54 MPa |
| S-chart lower / upper limits | 0 / 25.68 MPa |
| Lower-side Cpk / Ppk | 0.591 / 0.571 |
| Coupon failures | 1 of 12 (8.3%) |
| Flagged builds | None |
| Verdict | `not assessable`, because 4 builds are fewer than the default 25 |

The example is an **arithmetic validation**, not proof that a production process is acceptable. These expected results come from `SPEC.md`; rerun the command in your Codespace to verify your checkout.

## 6. Interpret the analysis

- **X-bar chart:** Each point is the mean tensile strength within a build. A mean below the lower control limit or above the upper control limit flags that build as potentially affected by special-cause variation.
- **S chart:** Each point is the sample standard deviation of coupons within a build. A standard deviation above the S-chart upper limit flags unusually high within-build variation.
- **Cpk (lower side):** Compares the build-mean grand average with the LSL using estimated short-term within-build variation. The code uses `Cpk = (grand_mean - LSL) / (3 × sigma_short)`.
- **Ppk (lower side):** Uses the overall sample standard deviation of all coupons in the denominator, reflecting total observed variation.
- **Failure rate:** `count(uts_mpa < LSL) / total_coupon_count`. This is the observed coupon failure fraction, not a forecast of future defects.
- **Shapiro-Wilk `p` value:** An additional normality diagnostic. A small p-value provides evidence against a normal distribution; it is not, by itself, a guarantee of normality or process stability.

**Control limits and specification limits are different.** Control limits are estimated from observed process variation. The user-entered LSL is an external customer requirement.
### Verdict logic

The backend returns a `verdict` plus a text `reason`:

1. **`not assessable`** if variation is zero so Cpk/Ppk are undefined, if any build is out of control, or if fewer than `min_builds` builds are present (checked in that order).
2. **`capable`** if the process passes those checks and `Cpk >= cpk_target`.
3. **`not capable`** if the process passes the preliminary checks but `Cpk < cpk_target`.

Numeric Cpk/Ppk values can still appear when the verdict is `not assessable`; do **not** interpret them as an approval. Optional LPBF parameters are descriptive investigation clues, not evidence of causality.

For formulas, response fields, and detailed endpoint documentation, see **[app/README.md](app/README.md)**.

## 7. REST API quick reference

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Service welcome message and documentation location. |
| `GET` | `/health` | Returns `{ "status": "ok" }`. |
| `GET` | `/datasets` | Lists `.csv` datasets currently bundled in `app/data/`. |
| `GET` | `/analyze?dataset=NAME&lsl=VALUE` | Analyzes a bundled CSV (only after files are synced). |
| `POST` | `/analyze` | Analyzes an uploaded CSV via multipart form-data. |
| `GET` | `/docs` | Interactive FastAPI / OpenAPI documentation. |

For both analysis routes, `min_builds` defaults to 25 and `cpk_target` to 1.33. Uploaded CSV requests send `file`, `lsl`, `min_builds`, and `cpk_target` as form fields. GET analysis accepts these as query parameters.

## 8. Test the code

After activating the virtual environment and installing requirements:

```bash
python -m pytest tests -q
```

This exercises the Python QC engine and API test suite. The task ledger records prior passing checks for H-03/H-04, but a new contributor should rerun this command on the current branch. Test execution is **not** equivalent to a verified public deployment or a complete React UI.

For details on Python functions, response keys, errors, and example programmatic usage, see [Backend and API documentation](app/README.md).

## 9. Demonstration datasets and walkthrough

The release plan calls for three **synthetic** datasets, each with 30 builds and three tensile-test coupons per build:

| Planned CSV | Intended behavior |
| --- | --- |
| `data/stable_capable.csv` | Stable process, lower-side Cpk at or above target. |
| `data/stable_incapable.csv` | Stable process, but lower-side Cpk below target. |
| `data/unstable_shift.csv` | A planted change from approximately build 20 and an unstable-process verdict. |

H-02 owns the CSV files and their units/column codebook at `data/README.md`. H-05 owns the step-by-step results and demo at `demo/README.md`, as well as the React frontend at `app/frontend/`.

**Demo walkthrough:** [demo/README.md](demo/README.md) (**pending H-05**; link will work after the team creates the file). Do not invent numeric results or screenshots before these datasets and the running dashboard have been verified.

## 10. Live deployment

**Posit Connect public URL:** **PENDING H-06**. Replace this status with the actual working, publicly accessible URL after the team validates it from a signed-out browser. **Do not paste a placeholder URL into the final Devpost submission.**

The backend's existing scripts are `app/manifestme.sh` and `app/deployme.sh`. Deployment preparation copies available CSV files with `app/sync_data.sh`. The H-06 owner is responsible for deployment configuration, credentials, and an HTTP-200 accessibility check; never store deployment API keys in this public repository.

## 11. Project layout

```text
team-sigma/
├── README.md                 # Project overview and contributor quick start (H-07)
├── SPEC.md                   # Binding MVP requirements and statistics
├── PROJECT_OVERVIEW.md       # Product context
├── CONTRACT.yaml             # Task ownership and completion checks
├── app/
│   ├── README.md             # Function, API, and backend documentation (H-07)
│   ├── qc.py                 # Statistical engine
│   ├── app.py                # FastAPI endpoints
│   ├── profiles/lpbf.py      # LPBF column mappings and optional parameters
│   ├── requirements.txt     # Pinned Python dependencies
│   ├── testme.sh             # Launch the API on port 8000
│   ├── sync_data.sh          # Copy demo CSVs into app/data/
│   ├── manifestme.sh         # Write a Posit Connect manifest
│   └── deployme.sh           # Deploy FastAPI to Posit Connect
├── tests/                    # Statistical and API tests
├── data/                     # Planned H-02 datasets and codebook
└── demo/                     # Planned H-05 demonstration and interpretation
```

`data/`, `demo/`, and `app/frontend/` are planned outputs and may not exist on the branch being viewed. Their presence and results must be confirmed before final delivery.

## 12. Reproducibility and project limits

For a fresh review, clone the public repository, create a Python virtual environment, install the pinned dependencies, run `python -m pytest tests -q`, launch `bash app/testme.sh`, and run the sample upload above. After H-02/H-05/H-06, also verify each dataset, demonstrate the React dashboard, and test the public URL.

The first release supports the LPBF profile, lower-bound strength specifications, equal-size build subgroups, X-bar/S special-cause flags, and descriptive comparisons of optional process parameters. It intentionally does not implement regression, ML forecasts, FMEA, hardware certification, mixed-size subgroups, or additional printing-process profiles.

**Project references:** [SPEC.md](SPEC.md) · [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) · [Task ledger](CONTRACT.yaml) · [Evaluation criteria](docs/criteria.md) · [Hackathon event](https://six-sigma-hackathon.devpost.com/).


---

![](docs/images/banner_icons.png)
