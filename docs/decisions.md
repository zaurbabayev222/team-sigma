# Design decisions and why

Sigma Airlines · Prompt 1, 3D Printing for Aerospace · agreed by the team on 2026-10-19

This is the reference for *why* the tool is built the way [`SPEC.md`](../SPEC.md) says. SPEC says
*what*; this file says *why*. If a decision changes, update both. Background: the review of
[`PROJECT_OVERVIEW.md`](../PROJECT_OVERVIEW.md) in [`plan-review.md`](plan-review.md) and the team's
[`AEROQUAL_REPOSITORY_ASSESSMENT.md`](../AEROQUAL_REPOSITORY_ASSESSMENT.md).

| # | Decision | Chosen |
|---|---|---|
| 1 | Core statistic | X-bar and S chart by build + lower-side Cpk/Ppk + coupon failure rate |
| 2 | Scope | LPBF only in release 1, designed so other processes plug in later |
| 3 | Inputs | Minimal: 3 required columns + the customer minimum; 3 optional parameters |
| 4 | Stack | FastAPI (Python) + React (Vite, plain JavaScript) |
| 5 | Expandability | Generic statistics + one process-profile file per printing process |

## 1. Core statistic

**Chosen:** an X-bar and S chart of tensile strength with one subgroup per build, lower-side
capability (Cpk) and performance (Ppk) against the customer minimum (LSL), and the share of coupons
that fail. Formulas and the hand-worked example are in SPEC section 4.

The tool answers the three questions the contractor actually has:

| Question | Statistic | Plain meaning |
|---|---|---|
| Is the process **stable**, or did something change? | X-bar and S chart | Each build is a point. A build outside the limits means something unusual happened in it. |
| Can the process **reliably meet** the minimum strength? | Cpk and Ppk (lower side) | How many standard deviations the average sits above the minimum, divided by 3. |
| How often do coupons **actually fail** today? | Failure rate | Coupons below the minimum ÷ all coupons. The prompt's complaint, as a number. |

**Why:**
- It matches the prompt's words: "monitor and flag when" is the control chart; "whether the
  printing process is capable" is Cpk.
- **Why one-sided:** strength has only a minimum. Stronger is never a defect, so there is no upper
  limit, and a two-sided Cp or Pp would need one invented. The course writes this as Cpk for the
  lower side (some books call it Cpl).
- **Why builds are the subgroups:** coupons printed in the same build share one machine run, so
  they are not independent tests. Treating each build as a subgroup measures the two kinds of
  variation separately: within a build (short-term) and between builds (shifts the chart flags).
- **Why X-bar and S, not X-bar and R:** the course textbook recommends the standard deviation over
  the range for measuring within-subgroup variation.
- **Why both Cpk and Ppk:** Cpk uses short-term variation (what the process *could* do if stable);
  Ppk uses all the variation (what it *is* doing). A big gap between them is itself a finding: the
  process is losing capability to instability.
- **Why the failure rate too:** it is what the customer sees. Capability predicts future failures;
  the failure rate counts today's. Both team documents asked for conformance.
- **Why "not assessable":** the course is clear that capability is meaningless on an unstable
  process. If any build is flagged, or there are fewer than 25 builds, the tool still shows the
  numbers but refuses to call the process capable, and says why.
- **Why 1.33:** the course's bare minimum is 1.0 (the spec exactly fits six standard deviations).
  1.33 is the common industry bar and suits "strict aerospace tolerances". It is a setting.

**Correction made on the way.** The first recommendation was an individuals (I-MR) chart of build
*averages*. Working the hand example showed a flaw: the customer's minimum applies to each coupon,
and averaging hides the spread inside a build, so capability would look better than it is. The tool
could say "capable" while coupons still fail. X-bar and S measures capability on individual coupons,
so the team switched to it. The cost is that every build must have the same number of coupons.

**Alternatives considered:**
- I-MR on one "witness coupon" per build: simplest math, but throws away the other coupons.
- I-MR on build averages: rejected, for the reason above.

## 2. Scope: LPBF only, ready to grow

**Chosen:** build for laser powder bed fusion (LPBF), the common titanium printing method the
overview already uses, and list other processes as future work.

**Why:**
- The rubric gives no points for breadth. It rewards one correct analysis that runs, deploys and is
  documented (50 of 100 points are "does it run" and "does it make sense").
- A full plug-in registry for five processes, as both team documents proposed, could take days of a
  7-day event.
- The team still wants to expand later, so release 1 keeps the one design rule that makes that
  cheap (decision 5).

## 3. Inputs: minimal

**Chosen:**
- **Required:** `build_id`, `build_date`, `uts_mpa` per coupon, and the customer minimum (LSL, MPa).
- **Optional:** `chamber_oxygen_ppm`, `powder_reuse_count`, `laser_power_w`.

**Why:**
- The rubric gives 5 points for asking only what the user can realistically provide, and takes
  them away for inputs the user is unlikely to know.
- The prompt says the contractor does not track enough parameters today, so a short list fits them.
- The optional parameters cover the "help contractors resolve these issues" part: for each flagged
  build, the tool shows which parameter moved. Chamber oxygen and powder reuse are well-known
  suspects for weak titanium parts, and both are already in the printer or powder logs.
- The full traceability list (machine, lot, heat treatment, orientation, test method and more) is a
  good *future* addition. It can arrive as optional columns without changing the statistics.

## 4. Stack: FastAPI + React (plain JavaScript)

**Chosen:** a FastAPI backend in Python and a React (Vite) dashboard in plain JavaScript.

**Why:**
- It is one of the delivery types the event allows, and judges get a page they can click through.
- The repo already has working starters for both (`demos/fastapi`, `demos/reactfront`), so the team
  starts from something that runs and deploys.
- Python computes every number; React only displays them. Both team documents require this, and it
  keeps the graded statistics in one tested place.
- TypeScript and Recharts are nice, but add setup on a 7-day clock. They can come later if a
  teammate already knows them.

## 5. How the build stays expandable

**Goal:** after release 1, adding another printing process (EB-PBF, DED, WAAM, binder jetting)
should take a small amount of new code, not a rework.

**The rule:** the statistics never know which printing process made the data.

```text
CSV upload
   |
   v
process profile  (app/profiles/lpbf.py: optional parameters, units, labels)
   |  maps the file to generic columns: subgroup, order, value, LSL
   v
statistics       (app/qc.py: X-bar/S, Cpk, Ppk, failure rate, verdict)
   |
   v
FastAPI          (app/app.py: passes the profile name through)
   |
   v
React page       (draws whatever parameters the profile lists)
```

- **`app/qc.py`** takes generic inputs: a subgroup id, an order, a measured value and a lower limit.
  It never mentions lasers, oxygen or powder. Tested once, it is reused by every process.
- **A process profile** is one small Python file that lists that process's optional parameters,
  each with a name, unit and label. LPBF's lists chamber oxygen, powder reuse and laser power.
- **The page** builds its parameter table from the profile's list, so a new profile needs no
  front-end change.
- **To add a process later:** write `app/profiles/<process>.py` with its parameters, add a test
  dataset for it, and register its name. `qc.py` and its tests do not change.
- **What release 1 does not build:** a profile selector with several entries, a configuration
  editor, or schema-validation machinery. Only the LPBF profile exists; the shape is what matters.

Other things that can grow the same way, without touching the statistics: an upper limit (for a
two-sided Cpk on dimensions), filters by machine or lot as optional columns, and unequal coupons per
build (would switch the S-chart constants to per-build values).

## H-10 update: user-approved LPBF plus WAAM

This supersedes the LPBF-only scope decision above for the new increment; the original release history remains recorded. The user approved one additional process before adding more statistics. Keep qc.py unchanged, use a profile registry and explicit process selection, preserve legacy LPBF defaults, and add three reproducible WAAM demonstration files. The section 4 SPEC known answer must match under both adapters; sampling design remains equal-size, comparable build subgroups. No automatic strength requirement, qualified operating window, parameter adjustment or training claim is introduced. Generic measurement-only files use the user's declared process; supplied tags and recognized foreign-profile fields are checked to prevent accidental pooling.
