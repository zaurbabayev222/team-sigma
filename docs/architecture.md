# How AeroQual works

Sigma Airlines · release 1 · 2026-10-19

Three pictures of the same app: who uses it ([use cases](#1-use-case-diagram)), what it does step by
step ([activity diagram](#2-activity-diagram)), and which function belongs to which subsystem
([FFBD](#3-functional-flow-block-diagram-ffbd)). The [subsystem table](#4-subsystems-and-who-builds-them)
maps each subsystem to a CONTRACT task and a teammate. Details live in [`SPEC.md`](../SPEC.md);
reasons in [`decisions.md`](decisions.md).

## 1. Use case diagram

```mermaid
flowchart LR
    QE["👤 Quality engineer"]
    JU["👤 Judge / reviewer"]
    PE["👤 Process engineer<br/>(future)"]

    subgraph AQ["AeroQual"]
        UC1(["Upload build test data (CSV)"])
        UC2(["Enter customer minimum strength (LSL)"])
        UC3(["Check stability: X-bar and S charts"])
        UC4(["Check capability: Cpk, Ppk, verdict"])
        UC5(["See coupon failure rate"])
        UC6(["Investigate flagged builds' parameters"])
        UC7(["Run the demo datasets"])
        UC8(["Add a new printing-process profile"])
    end

    QE --- UC1
    QE --- UC2
    QE --- UC3
    QE --- UC4
    QE --- UC5
    QE --- UC6
    JU --- UC7
    PE -.- UC8
    UC7 -. includes .-> UC3
    UC7 -. includes .-> UC4
```

The quality engineer is the one user release 1 is built for. Judges use the same page through the
demo datasets. Adding a process profile is a future use case (dashed); release 1 only makes it
cheap.

## 2. Activity diagram

```mermaid
flowchart TD
    S([Start]) --> A1[Choose a demo dataset or upload a CSV]
    A1 --> A2[Enter customer minimum strength, LSL in MPa]
    A2 --> D1{File valid?<br/>required columns, no blank uts_mpa,<br/>equal coupons per build, 2+ builds}
    D1 -- no --> E1[Show the error, naming the row or build] --> A1
    D1 -- yes --> A3[Map columns through the LPBF process profile]
    A3 --> A4[Sort builds by build_date]
    A4 --> A5[Per build: mean and standard deviation]
    A5 --> A6[Control limits: X-bar and S charts]
    A6 --> A7[Flag builds outside the limits]
    A7 --> A8[Cpk and Ppk, lower side; failure rate; normality check]
    A8 --> D2{Any build flagged?}
    D2 -- yes --> V1[Verdict: not assessable, unstable]
    D2 -- no --> D3{25 or more builds?}
    D3 -- no --> V2[Verdict: not assessable, too few builds]
    D3 -- yes --> D4{Cpk at least 1.33?}
    D4 -- yes --> V3[Verdict: capable]
    D4 -- no --> V4[Verdict: not capable]
    V1 --> A9[Parameter table for flagged builds]
    V2 --> A10
    V3 --> A10
    V4 --> A10
    A9 --> A10[Show charts, numbers, verdict and reason]
    A10 --> F([End])
```

Every path ends with the numbers on screen. Only the verdict changes, and it always says why.

## 3. Functional flow block diagram (FFBD)

Top level. Each block is a function; the colour band is the subsystem that owns it (section 4).

```mermaid
flowchart LR
    F1["1.0<br/>Receive inputs<br/>(CSV + LSL)"] --> F2["2.0<br/>Validate data"]
    F2 --> F3["3.0<br/>Map via process profile"]
    F3 --> F4["4.0<br/>Compute statistics"]
    F4 --> F5["5.0<br/>Decide verdict"]
    F5 --> F6["6.0<br/>Build investigation table"]
    F6 --> F7["7.0<br/>Display results"]

    classDef ui fill:#e7f1fb,stroke:#4a78b5,color:#000
    classDef api fill:#f9eeda,stroke:#b5874a,color:#000
    classDef stats fill:#e5f4e4,stroke:#4a9a52,color:#000
    class F1,F7 ui
    class F2,F3,F6 api
    class F4,F5 stats
```

Blue = front end · amber = API and profile · green = statistics engine.

Function 4.0 broken down (all inside `app/qc.py`, no web code):

```mermaid
flowchart LR
    G1["4.1<br/>Per-build mean and s"] --> G2["4.2<br/>X̿, s̄, c4, A3, B3, B4"]
    G2 --> G3["4.3<br/>X-bar and S limits"]
    G3 --> G4["4.4<br/>Flag builds"]
    G2 --> G5["4.5<br/>σ_short, σ_total,<br/>Cpk and Ppk lower"]
    G1 --> G6["4.6<br/>Failure rate"]
    G1 --> G7["4.7<br/>Shapiro-Wilk"]
    G4 --> G8["5.0<br/>Verdict"]
    G5 --> G8
```

## 4. Subsystems and who builds them

| Subsystem | Functions | CONTRACT task | Files it owns | Teammate |
|---|---|---|---|---|
| Statistics engine | 4.0, 5.0 | H-03 | `app/qc.py`, `tests/` | A |
| Test data and codebook | test inputs for 1.0 | H-02 | `data/` | B |
| API and process profile | 2.0, 3.0, 6.0 | H-04 | `app/` except A's files | C |
| Front end and demo | 1.0, 7.0 | H-05 | `app/frontend/`, `demo/` | D |
| Deploy | public URL | H-06 | `.github/`, `app/manifest.json` | C |
| Docs and submission | README, repo check, Devpost | H-07, H-08 | `README.md`, `app/README.md`, `.gitignore` | B |

**The two interfaces everyone builds against**, agreed first and written in `docs/plan.md`:

1. **Data columns** (between B, C and A): `build_id`, `build_date`, `uts_mpa`, plus the optional
   LPBF parameters. SPEC section 3.
2. **What `qc.py` returns** (between A, C and D): one result object with the per-build points,
   the limits, Cpk, Ppk, the failure rate, the flags, the verdict and its reason. C passes it
   through the API as JSON; D draws it.

With those two fixed, all four can work at once:

```mermaid
flowchart LR
    P["docs/plan.md<br/>interfaces agreed<br/>(all four)"] --> A["A: H-03 statistics"]
    P --> B["B: H-02 data"]
    P --> C["C: H-04 API, using a<br/>fake result until H-03 lands"]
    P --> D["D: H-05 page, drawing<br/>a sample JSON result"]
    A --> I["Join: API calls real qc.py"]
    B --> I
    C --> I
    I --> R["C: H-06 deploy"]
    D --> R
    R --> W["B: H-07 README, H-08 submit"]
```
