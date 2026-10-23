# How AeroQual works

Sigma Airlines · updated 2026-10-22 (release 1 plus the approved extensions H-10 to H-17)

Pictures of the same app: who uses it ([use cases](#1-use-case-diagram)), what it does step by
step ([activity diagram](#2-activity-diagram)), and which function belongs to which part of the code
([FFBD](#3-functional-flow-block-diagram-ffbd)). [Section 4](#4-subsystems)
maps each subsystem to its functions, CONTRACT tasks and files. Details live in
[`SPEC.md`](../SPEC.md); reasons in [`decisions.md`](decisions.md).

The [offline walkthrough](../demo/slidedeck/index.html) is a documentation artifact outside `app/`.
`demo/build_slidedeck.py` captures verified API outputs and exact synthetic CSVs into `deck-data.json`,
then inlines the template, styles, JavaScript and data into one HTML file. It has no external library,
network dependency or browser-side QC calculation. Actual uploads remain in the React/FastAPI app.
Current evidence and open release gates are in [evaluation.md](evaluation.md) and
[remaining-work.md](remaining-work.md).

Each diagram has an image link under it, in case GitHub draws the Mermaid code badly. The images
are exported from the code: after editing a diagram, regenerate its image with
`npx -y @mermaid-js/mermaid-cli@11.4.2 -i <diagram>.mmd -o docs/images/diagram-<name>.png -b white -s 2`.

## 1. Use case diagram

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 22, "rankSpacing": 60}}}%%
flowchart LR
    QE["Quality<br>engineer"]

    subgraph AQ["AeroQual"]
        direction TB
        UC0(["Choose printing<br>process"])
        UC1(["Upload build test<br>data or pick example"])
        UC2(["Enter customer<br>minimum strength"])
        UC3(["Check stability<br>(control charts)"])
        UC4(["Check capability<br>(Cpk, Ppk)"])
        UC5(["See coupon<br>failure rate"])
        UC6(["Rank chart signals<br>and defects (Pareto)"])
        UC7(["Follow investigation<br>actions"])
        UC8(["Narrow to a<br>date range"])
        UC9(["Run the example<br>datasets"])
        UC10(["Work through the<br>offline tutorial"])
        UC11(["Add a process<br>profile"])
    end

    JU["Judge or<br>reviewer"]
    DEV["Developer"]

    QE --- UC0 & UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
    UC9 --- JU
    UC10 --- JU
    UC11 --- DEV
```

[Open this diagram as an image](images/diagram-use-case.png)

The quality engineer is the user the tool is built for. Judges use the same dashboard through the
example datasets, or the offline tutorial. A developer adds a printing process by writing one profile
file in `app/profiles/` and registering it; four exist (LPBF, WAAM, EB-PBF, powder-fed laser DED).

## 2. Activity diagram

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 40, "rankSpacing": 40}}}%%
flowchart TD
    S([Start]) --> A0["Choose process: LPBF,<br>WAAM, EB-PBF or<br>laser DED"]
    A0 --> A1["Pick an example<br>or upload a CSV"]
    A1 --> A2["Enter customer<br>minimum (LSL, MPa)"]
    A2 --> D1{"File<br>valid?"}
    D1 -- no --> E1["Show the error,<br>naming the row"]
    E1 --> A1
    D1 -- yes --> A3["Map columns via<br>the selected profile"]
    A3 --> A4["Sort builds<br>by date"]
    A4 --> A5["Mean and std dev<br>of each build"]
    A5 --> A6["X-bar and S<br>control limits"]
    A6 --> A7["Flag builds<br>outside limits"]
    A7 --> A8["Cpk, Ppk,<br>failure rate,<br>normality check"]
    A8 --> D0{"Any<br>variation?"}
    D0 -- no --> V0["Not assessable:<br>no variation"]
    D0 -- yes --> D2{"Any build<br>flagged?"}
    D2 -- yes --> V1["Not assessable:<br>unstable"]
    D2 -- no --> D3{"25+<br>builds?"}
    D3 -- no --> V2["Not assessable:<br>too few builds"]
    D3 -- yes --> D4{"Cpk<br>≥ 1.33?"}
    D4 -- yes --> V3["Capable"]
    D4 -- no --> V4["Not capable"]
    V0 --> A9
    V1 --> A9
    V2 --> A9
    V3 --> A9
    V4 --> A9
    A9["Signal and defect<br>Pareto, parameters,<br>investigation actions"] --> A10["Show charts,<br>numbers, verdict<br>and reason"]
    A10 --> D5{"Apply a date<br>range or pick<br>a Pareto bar?"}
    D5 -- yes --> A11["Recount the Pareto<br>for that view, same<br>full-log limits"]
    A11 --> A10
    D5 -- no --> F([End])
```

[Open this diagram as an image](images/diagram-activity.png)

"File valid?" checks the required columns, that no `uts_mpa` is blank or non-numeric, that every
build has one date and the same number of coupons, that there are at least 2 builds, and that the
data match the chosen process. Every path ends with the numbers on screen. Only the verdict
changes, and it always says why. A date range or a Pareto selection changes only the investigation
view: limits, Cpk, Ppk and the verdict always come from the complete file.

## 3. Functional flow block diagram (FFBD)

Top level. Each block is a function; its colour is the part of the code that owns it.

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 40}}}%%
flowchart LR
    F1["1.0<br>Receive<br>inputs"] --> F2["2.0<br>Validate<br>data"]
    F2 --> F3["3.0<br>Map via<br>profile"]
    F3 --> F4["4.0<br>Compute<br>statistics"]
    F4 --> F5["5.0<br>Decide<br>verdict"]
    F5 --> F6["6.0<br>Investigation<br>evidence"]
    F6 --> F7["7.0<br>Display<br>results"]
    F7 -. optional .-> F8["8.0<br>Filtered<br>view"]
    F8 -.-> F7

    classDef ui fill:#e7f1fb,stroke:#4a78b5,color:#000
    classDef api fill:#f9eeda,stroke:#b5874a,color:#000
    classDef stats fill:#e5f4e4,stroke:#4a9a52,color:#000
    classDef helper fill:#f0e9f7,stroke:#7a5aa8,color:#000
    class F1,F7 ui
    class F2,F3 api
    class F4,F5 stats
    class F6,F8 helper
```

[Open this diagram as an image](images/diagram-ffbd.png)

Blue = front end (`app/frontend/`) · amber = API and process profiles (`app/app.py`,
`app/profiles/`) · green = statistics engine (`app/qc.py`) · purple = descriptive investigation
helpers (plain Python, no new statistics).

Function 4.0 broken down (all inside `app/qc.py`, no web code):

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 50}}}%%
flowchart LR
    G1["4.1<br>Mean and s<br>per build"] --> G2["4.2<br>Grand mean,<br>avg s, constants"]
    G2 --> G3["4.3<br>X-bar and S<br>limits"]
    G3 --> G4["4.4<br>Flag<br>builds"]
    G2 --> G5["4.5<br>Cpk and Ppk<br>(lower side)"]
    G1 --> G6["4.6<br>Failure<br>rate"]
    G1 --> G7["4.7<br>Normality<br>check"]
    G4 --> G8["5.0<br>Verdict"]
    G5 --> G8
```

[Open this diagram as an image](images/diagram-ffbd-statistics.png)

The constants in 4.2 are c4, A3, B3 and B4, computed from the number of coupons per build. The
normality check in 4.7 is a Shapiro-Wilk test.

Functions 6.0 and 8.0 broken down. They count and describe; they never change a limit or an index:

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 50}}}%%
flowchart LR
    R["5.0<br>Verdict and<br>full-log limits"] --> H1["6.1<br>Signal Pareto<br>signals.py"]
    R --> H2["6.2<br>Inspection Pareto<br>inspection.py"]
    R --> H3["6.3<br>Parameter summary<br>app.py"]
    R --> H4["6.4<br>Investigation actions<br>investigation.py"]
    H1 --> H5["8.0<br>Date-window and<br>selection views<br>pareto_view.py"]
    H2 --> H5

    classDef stats fill:#e5f4e4,stroke:#4a9a52,color:#000
    classDef helper fill:#f0e9f7,stroke:#7a5aa8,color:#000
    class R stats
    class H1,H2,H3,H4,H5 helper
```

[Open this diagram as an image](images/diagram-ffbd-investigation.png)

## 4. Subsystems

| Subsystem | Functions | CONTRACT tasks | Main files |
|---|---|---|---|
| Statistics engine | 4.0, 5.0 | H-03, H-17 | `app/qc.py`, `tests/` |
| Investigation helpers | 6.0, 8.0 | H-11, H-12, H-14 | `app/signals.py`, `app/inspection.py`, `app/investigation.py`, `app/pareto_view.py` |
| Test data and codebook | test inputs for 1.0 | H-02, H-10, H-13, H-14 | `data/` |
| API and process profiles | 2.0, 3.0 | H-04, H-10, H-13 | `app/app.py`, `app/profiles/` |
| Front end and demo | 1.0, 7.0 | H-05, H-15, H-16 | `app/frontend/`, `demo/` |
| Deploy | public URL | H-06, H-09 | `.github/`, `app/manifest.json` |
| Docs and submission | README, repo check, Devpost | H-01, H-07, H-08 | `SPEC.md`, `PROJECT_OVERVIEW.md`, `README.md`, `app/README.md`, `docs/`, `.gitignore` |

**The two interfaces everyone built against**, agreed first and written in `docs/plan.md`:

1. **Data columns:** `build_id`, `build_date`, `uts_mpa`, plus the optional parameters of the
   selected process profile. SPEC section 3.
2. **What `qc.py` returns:** one result object with the per-build points, the limits, Cpk, Ppk,
   the failure rate, the flags, the verdict and its reason. The API adds the investigation helpers'
   output and passes it on as JSON; the front end draws it.

### Original work plan (Oct 19, historical)

Before anyone claimed tasks, the plan split the work into four parallel roles (A to D). Teammates
then claimed tasks freely, so the roles below do not show who did what; the Git history and
[`CONTRACT.yaml`](../CONTRACT.yaml) do.

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 50}}}%%
flowchart LR
    P["docs/plan.md<br>interfaces agreed<br>(all four)"] --> A["A: H-03<br>statistics"]
    P --> B["B: H-02<br>test data"]
    P --> C["C: H-04 API<br>(fake result<br>until H-03)"]
    P --> D["D: H-05 page<br>(sample JSON<br>result)"]
    A --> I["Join: API<br>calls real qc.py"]
    B --> I
    C --> I
    I --> R["C: H-06<br>deploy"]
    D --> R
    R --> W["B: H-07 README,<br>H-08 submit"]
```

[Open this diagram as an image](images/diagram-parallel-work.png)

## H-10 process selection

The browser loads GET /profiles and the selected process catalog from GET /datasets?process_type=.... Profile metadata supplies optional parameter names and units. GET /analyze uses a query parameter; POST /analyze uses a multipart process_type field. Both default to LPBF for older clients. profiles/__init__.py registers LPBF/WAAM and their six explicit example IDs. app.py validates process compatibility, passes only subgroup/order/value mappings into the unchanged qc.analyze function, and appends selected-profile context and histogram bins. No process-specific statistical engine is duplicated.

The upload snapshot includes process, dataset/file and LSL. Switching profiles clears an upload and marks older results stale. Example catalog cleanup ignores obsolete responses, so a delayed LPBF catalog cannot overwrite a WAAM selection. The deployment bundle includes both profile modules, registry and all six CSVs; isolated HTTP verification runs all six through demo/check.py.


## H-11 to H-13: signal and investigation flow

The API calls unchanged qc.analyze, then plain signals.signal_pareto and investigation.investigation_actions before serializing. React renders Python counts, percentages and action evidence; it computes only plot geometry/formatting. EB-PBF and powder-fed laser DED are registered profiles; dataset filtering, shared-field units and mismatch checks apply to all four. Twelve CSVs, both new helper modules and all four profile modules ship in the flat Connect bundle. See [the response contract](signal-investigation.md).


## H-14: fixed-limit investigation views

The API first performs complete-file analysis, then inspection_records/inspection_pareto and pareto_view produce read-only descriptive views. Filtering reuses original limits and includes inclusive source dates, scoped signal/inspection denominators, selected build/coupon context and focused actions. React submits the complete original dataset/file with optional view fields; no upload retention or database is added. A category selection narrows details, not the Pareto denominator. Four distinct synthetic inspection files supplement the unchanged twelve original CSVs. See [the view contract](pareto-explorer.md).
