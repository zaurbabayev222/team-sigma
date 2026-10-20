# How AeroQual works

Sigma Airlines · release 1 · 2026-10-19

Three pictures of the same app: who uses it ([use cases](#1-use-case-diagram)), what it does step by
step ([activity diagram](#2-activity-diagram)), and which function belongs to which subsystem
([FFBD](#3-functional-flow-block-diagram-ffbd)). The [subsystem table](#4-subsystems-and-who-builds-them)
maps each subsystem to a CONTRACT task and a teammate. Details live in [`SPEC.md`](../SPEC.md);
reasons in [`decisions.md`](decisions.md).

Each diagram has an image link under it, in case GitHub draws the Mermaid code badly. The images
are exported from the code: after editing a diagram, regenerate its image with
`npx -y @mermaid-js/mermaid-cli@11.4.2 -i <diagram>.mmd -o docs/images/diagram-<name>.png -b white -s 2`.

## 1. Use case diagram

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 70}}}%%
flowchart LR
    QE["Quality<br>engineer"]
    JU["Judge or<br>reviewer"]
    PE["Process engineer<br>(future)"]

    subgraph AQ["AeroQual"]
        UC1(["Upload build<br>test data"])
        UC2(["Enter customer<br>minimum strength"])
        UC3(["Check stability<br>(control charts)"])
        UC4(["Check capability<br>(Cpk, Ppk)"])
        UC5(["See coupon<br>failure rate"])
        UC6(["Investigate<br>flagged builds"])
        UC7(["Run the demo<br>datasets"])
        UC8(["Add a printing<br>process profile"])
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

[Open this diagram as an image](images/diagram-use-case.png)

The quality engineer is the one user release 1 is built for. Judges use the same page through the
demo datasets. Adding a process profile is a future use case (dashed); release 1 only makes it
cheap.

## 2. Activity diagram

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 40, "rankSpacing": 40}}}%%
flowchart TD
    S([Start]) --> A1["Choose demo data<br>or upload a CSV"]
    A1 --> A2["Enter customer<br>minimum (LSL, MPa)"]
    A2 --> D1{"File<br>valid?"}
    D1 -- no --> E1["Show the error,<br>naming the row"]
    E1 --> A1
    D1 -- yes --> A3["Map columns via<br>LPBF profile"]
    A3 --> A4["Sort builds<br>by date"]
    A4 --> A5["Mean and std dev<br>of each build"]
    A5 --> A6["X-bar and S<br>control limits"]
    A6 --> A7["Flag builds<br>outside limits"]
    A7 --> A8["Cpk, Ppk,<br>failure rate,<br>normality check"]
    A8 --> D2{"Any build<br>flagged?"}
    D2 -- yes --> V1["Not assessable:<br>unstable"]
    D2 -- no --> D3{"25+<br>builds?"}
    D3 -- no --> V2["Not assessable:<br>too few builds"]
    D3 -- yes --> D4{"Cpk<br>≥ 1.33?"}
    D4 -- yes --> V3["Capable"]
    D4 -- no --> V4["Not capable"]
    V1 --> A9["Parameter table<br>for flagged builds"]
    A9 --> A10["Show charts,<br>numbers, verdict<br>and reason"]
    V2 --> A10
    V3 --> A10
    V4 --> A10
    A10 --> F([End])
```

[Open this diagram as an image](images/diagram-activity.png)

"File valid?" checks four things: the required columns are present, no `uts_mpa` is blank, every
build has the same number of coupons, and there are at least 2 builds. Every path ends with the
numbers on screen. Only the verdict changes, and it always says why.

## 3. Functional flow block diagram (FFBD)

Top level. Each block is a function; its colour is the subsystem that owns it (section 4).

```mermaid
%%{init: {"flowchart": {"padding": 20, "nodeSpacing": 30, "rankSpacing": 40}}}%%
flowchart LR
    F1["1.0<br>Receive<br>inputs"] --> F2["2.0<br>Validate<br>data"]
    F2 --> F3["3.0<br>Map via<br>profile"]
    F3 --> F4["4.0<br>Compute<br>statistics"]
    F4 --> F5["5.0<br>Decide<br>verdict"]
    F5 --> F6["6.0<br>Investigation<br>table"]
    F6 --> F7["7.0<br>Display<br>results"]

    classDef ui fill:#e7f1fb,stroke:#4a78b5,color:#000
    classDef api fill:#f9eeda,stroke:#b5874a,color:#000
    classDef stats fill:#e5f4e4,stroke:#4a9a52,color:#000
    class F1,F7 ui
    class F2,F3,F6 api
    class F4,F5 stats
```

[Open this diagram as an image](images/diagram-ffbd.png)

Blue = front end · amber = API and profile · green = statistics engine.

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
