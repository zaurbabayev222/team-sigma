# AeroQual engineering brief

Artifact: **[`../aeroqual_brief.html`](../aeroqual_brief.html)**. Download/open the HTML directly in
a browser; all styles, interaction code and verified data are embedded. No backend or internet
connection is required to use the presentation. GitHub's HTML source preview is not the presentation.

Six spreads: Decision, Platform, Evidence, Comparison, Investigation and Engineering value. Method and
scenario selections persist between spreads. Evidence offers X-bar, S, strength distribution, signal
Pareto and inspection Pareto views. Hover/focus reveals values; activating a build point or category
selects evidence for investigation. Comparison has independent reference/comparison scenario selectors.
Native buttons, Tab/Enter/Space and section links work; arrow keys, Page Up/Down and Home/End navigate
when focus is outside controls. Reduced motion is respected. Print expands all six spreads and the
technical appendix using the selected method/scenario and comparison choices.

## Source and reproduction

From the repository root with `app/requirements.txt` installed:

```powershell
python demo/brief_source/build_brief.py --capture
python demo/brief_source/build_brief.py --check
python -m pytest tests/test_engineering_brief.py
```

`--capture` calls the real FastAPI `POST /analyze` endpoint through its in-process TestClient for all
16 repository CSVs at illustrative LSL 895 MPa. It requires the analysis modules, profiles and CSVs to
match their committed Git bytes. Each response's core fields are compared to `app.qc.analyze` before
writing `snapshot.json`. Exact full commit/origin-main hashes, UTC capture time, source/data SHA-256
hashes, raw source records and profile metadata are included. No running API server is needed, and no
application data files are copied or changed. The existing TestClient/httpx deprecation warning may appear.

Building without `--capture` reuses the snapshot. `--check` requires current source/data hashes and exact
generated HTML equivalence. It does not recalculate backend results. The test suite independently
compares all captured core results to the engine and source coupon strengths to the repository CSVs.
JavaScript formats data and draws geometry; it never recalculates QC statistics or histogram bins.

The inspection sample is a **separate fourth dataset** per method. Selecting it updates the entire
brief and source label, rather than silently attaching defect labels to another scenario. Blanks and
explicit `none` remain distinct. Stable strength datasets without inspection fields show an honest
empty inspection state with a working action to select the labeled sample.

## Dashboard link and local preview

The default **Open dashboard** link is `http://127.0.0.1:8001/dashboard/`, a separate local app preview.
It is not evidence of a public deployment. If needed, complete the root README setup and start:

```powershell
python -m uvicorn app.app:app --host 127.0.0.1 --port 8001
```

To choose an already verified public dashboard URL, rebuild with `--dashboard-url` and that address;
do not embed private server URLs, credentials or tokens. The HTML itself does not connect to the API.
For the brief, double-click the artifact or run this narrowly scoped static server:

```powershell
python -m http.server 8012 --bind 127.0.0.1 --directory demo
```

Then open `http://127.0.0.1:8012/aeroqual_brief.html`. This serves only `demo/`, not the repository root.
Stopping the server does not affect a downloaded/local-file copy of the brief.

## Interpretation and scope

The brief withholds capability on unstable logs while retaining descriptive Cpk/Ppk. Statistical control
limits are separate from the customer LSL. Recorded process ranges are descriptive, not approved
operating windows. Recommendations are backend investigation checks, not causal proof, setpoints,
flightworthiness judgments or release authority. Snapshot status is visible throughout the briefing.

H-16 adds only this artifact, this source directory, its new test module and its ledger entry. Existing
H-05 tutorial/demo README/frontend, app/runtime/statistics, data and H-06 files remain unchanged.
The user subsequently accepted the brief and approved committing/pushing this isolated increment
to main. Deployment remains outside this task.
