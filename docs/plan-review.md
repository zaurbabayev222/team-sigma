# AeroQual Plan Review

2026-10-19 · Zaur Babayev

> **For information only.** This is a review of [`PROJECT_OVERVIEW.md`](../PROJECT_OVERVIEW.md), not a
> decision. Nothing here is agreed until the team signs off; agreed choices go into
> [`SPEC.md`](../SPEC.md) and `docs/plan.md`.

PROJECT_OVERVIEW.md targets Prompt 1 (3D Printing for Aerospace) with sound statistics, but it is sized
for a semester, not a 7-day hackathon. Keep the core (a control chart plus a one-sided capability index
on titanium tensile strength) and cut about two thirds of the rest.

## What to keep

The core idea and its statistical care are worth keeping as they are.

- **Matches the prompt.** It covers failing strength tests, linking process and environment data to
  strength, capability, flagging problems and helping resolve them.
- **Sound statistics.** Control limits are not specification limits. A minimum-strength spec gets a
  one-sided Cpl, with no invented upper limit. Within-sigma (Cp/Cpk) stays separate from overall sigma
  (Pp/Ppk). Coupons from one build are not treated as independent. A missing test is not a pass. No
  capability verdict when the process is unstable. This protects the 25 points for valid QC analysis.
- **Three synthetic scenarios** (stable and capable, stable but incapable, unstable) are exactly the 2–3
  test datasets the rubric asks for, each showing a different verdict.
- **Honest framing.** Data is labelled synthetic, and the tool does not certify hardware.
- **Allowed stack.** FastAPI plus React is one of the permitted delivery types.

## What to improve

Scope is the main problem; the other six changes make the plan specific enough to build and test.

1. **Cut the scope.** The plan has 4 dashboard modules, regression, ANOVA, FMEA, schema validation and a
   registry for 5 printing technologies. The rubric gives no points for breadth. It rewards one correct
   analysis that runs, deploys and is documented. Build for LPBF (laser powder bed fusion) only, and
   mention other technologies in one "future work" line.
2. **Fewer inputs (5 pts).** The plan lists 13 traceability fields, 6 outcome fields and 6 process
   parameters.
    - Required: `build_id`, build order or date, `uts_mpa` per coupon, and the customer's minimum
      strength (LSL).
    - Optional: 2–3 process parameters, for example chamber oxygen, powder reuse count, laser power.
    - Cut everything else.
3. **Name one user and one decision (5 pts).** "Engineers" is too broad. Example: the quality engineer
   reviewing each finished build decides whether the process can meet the strength spec, and if not,
   which parameter to investigate first.
4. **Make the capability rules concrete.** Turn "only when stable and sufficient" into rules a test can
   check:
    - no points outside the control limits
    - at least 25 builds
    - a normality check (histogram plus Shapiro-Wilk)
    - "capable" means Cpl ≥ 1.33, with the threshold adjustable
    - unit of analysis: an I-MR chart of build-average UTS; datasets of about 25–30 builds with 3–5
      coupons each
5. **One analysis for "help resolve", not five.** Correlate each optional process parameter with
   build-average UTS, and show which builds and parameters moved when the process went out of control.
6. **Address "tolerances".** Strength is a one-sided spec and stays the core. A two-sided Cpk on
   dimensional deviation can come later, only after the strength analysis passes review.
7. **Make deployment real.** The rubric needs a live URL on Posit Connect. FastAPI plus React means two
   deploys; the repo has a workflow for each. Plain JavaScript instead of TypeScript matches the React
   demo and saves setup time.

## Revised scope

Build the Must tier first and deploy it; move down a tier only when the one above passes review.

| Tier | What's in it |
| --- | --- |
| Must (MVP) | I-MR chart of build-average UTS; Cpl/Ppl against the LSL; a "capable / not capable / not assessable" verdict with reasons; FastAPI plus a one-page React view; 3 datasets plus codebook; deployed |
| Should | Process-parameter panel: correlation of oxygen, powder reuse and laser power with UTS, with out-of-control builds highlighted |
| Could | Two-sided Cpk on dimensional deviation; filters by machine or lot; a build investigation table |
| Cut | Multi-technology registry; regression with diagnostics; ANOVA; FMEA; schema validation framework |

## Work split (draft)

Each CONTRACT task owns its own files, so four people can work in parallel without editing the same
ones.

| Person | Tasks | Files they own |
| --- | --- | --- |
| A | H-03: the statistics function and its tests (most important) | `app/qc.py`, `tests/` |
| B | H-02: the 3 test datasets and the codebook | `data/` |
| C | H-04: the API that calls A's function; then H-06: deploy | `app/` (except A's files), `.github/` |
| D | H-05: the dashboard and demo walkthrough; then H-07: the README | `app/frontend/`, `demo/`, `README.md` |

Before splitting up, agree on the data columns (so B's CSVs match what A's function reads) and on what
the function returns (so C and D know what to display). Both go in `docs/plan.md`.

## Decisions for the team

Settle these together before anyone builds; tick each one off when agreed.

- [ ] Accept the Must / Should / Could / Cut scope above, or change it
- [ ] Core statistic: I-MR chart plus one-sided Cpl/Ppl on build-average UTS (recommended), or another choice
- [ ] Stack: FastAPI plus React (recommended), FastAPI only, or a Python Shiny dashboard
- [ ] Who takes roles A, B, C and D
- [ ] Make the team-sigma repo public, so judges can open it and the deploy can run
- [ ] Update PROJECT_OVERVIEW.md, or move the agreed plan into SPEC.md
