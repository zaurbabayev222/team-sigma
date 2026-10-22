# Evaluation evidence

This maps the **unchanged 100-point rubric** in [criteria.md](criteria.md) to AeroQual evidence.
It is an evidence inventory, not a self-awarded score. Local checks do not establish publication,
independent review, deployment or submission. See [remaining-work.md](remaining-work.md).

| Rubric item | Points | Current evidence | Remaining confirmation |
| --- | ---: | --- | --- |
| Effective, working tool | 25 | FastAPI + React; [Windows setup](../README.md); all 16 API scenarios match the Python engine; UI tests/build | Independent run of the published candidate; public availability is H-06 |
| Valid QC analyses in Python/R | 25 | [qc.py](../app/qc.py), [SPEC section 4](../SPEC.md), [known-answer and degenerate tests](../tests/); pure tested signal/inspection/view helpers | Team explanation of assumptions and limits; no claim of hardware qualification |
| Prompt fit | 5 | Prompt 1, aerospace 3D printing; [SPEC](../SPEC.md), [overview](../PROJECT_OVERVIEW.md) | Final narrative review |
| Clear user and use case | 5 | Quality engineer reviewing titanium build/coupon tensile tests; stability, capability and failures separated | Independent usability feedback |
| Minimal, reasonable inputs | 5 | Three required CSV columns plus customer LSL; optional process context and primary defect; [API reference](../app/README.md) | Check actual customer sampling and measurement suitability |
| Clear test-data demonstration | 10 | [14-lesson interactive HTML deck](../demo/slidedeck/index.html), [written walkthrough](../demo/README.md), [API parity runner](../demo/check.py) | Independent teammate follows and reproduces it (H-05) |
| Excellent documentation | 10 | [README](../README.md), [function/API reference](../app/README.md), [architecture](architecture.md), [Pareto guide](pareto-explorer.md), [tutorial instructions](../demo/README.md) | Independent fresh-clone review and live URL gate (H-07/H-06) |
| 2–3 accurate working test datasets | 5 | Original three LPBF examples provide capable/incapable/unstable cases; 13 supplementary examples extend methods and inspections; four validators | Reviewed check-in; synthetic data must remain labeled |
| Dataset codebook and README | 5 | [data/README.md](../data/README.md): columns, units, seeds, collection guidance, missing/none semantics | Final independent readability check |
| Fully reproducible public repository | 5 | Locked frontend dependencies, pinned Python dependencies, startup scripts; clean local committed-baseline clone and fresh dependency checks | Publish current candidate, reproduce that public revision and confirm Devpost (H-08) |
| **Total** | **100** | **Coverage is mapped; points are awarded by event staff.** | |

## Local verification, 22 October 2026

Checks use Python 3.12 in an isolated, newly created project-local environment. These are agent-run
checks, not independent teammate acceptance.

```powershell
python -m pytest tests -q
python data/validate.py
python data/validate_waam.py
python data/validate_additional.py
python data/validate_inspection.py
python demo/check.py --base-url http://127.0.0.1:8001
python demo/build_slidedeck.py --check
npm.cmd --prefix app/frontend test
npm.cmd --prefix app/frontend run build
```

Python output: `78 passed, 1 warning, 18 subtests passed`. The warning is the existing
Starlette/TestClient deprecation concerning httpx; no dependency upgrade is included in this task.
Validators report `PASS` for schemas, independent arithmetic, scenario outcomes and reproducibility.
API runner prints `PASS: all sixteen synthetic scenarios (LPBF + WAAM + EB-PBF + laser DED) and API parity.`
The offline artifact check prints `Offline deck matches sources and captured API/data hashes: PASS`.
Frontend output: `Tests 19 passed (19)` and `built in 7.85s` (Vite production build).

The tutorial browser checks cover 14 lessons, all 16 scenario selections, LSL experiments, captured date
views, keyboard navigation/category selection, feedback, exact CSV downloads, offline opening, responsive
layout and printing. They supplement the H-14 app browser evidence; the deck is not a second QC engine.

## Statistical interpretation boundaries

- Control limits come from the full input, including signaled builds; they are not customer specifications.
- A date/category view does not refit limits or change full-log indices, verdict or observed failure totals.
- Stability, minimum build count and usable variation gate a capability verdict. Diagnostic indices alone
  do not override that gate. Lower-only Cpk/Ppk are not two-sided capability claims.
- Signal Pareto shares use signal occurrences; a build can contribute two signals. Inspection Pareto shares
  use coupons with a recorded primary defect. `none`, blank and below-LSL are different concepts.
- Recommendations propose investigation checks. Frequency, correlation, synthetic shifts and pooled
  Shapiro–Wilk results do not identify a physical cause or validate a parameter adjustment.

## Reproducibility scope

A clean local Git clone of committed revision `3fa4c7c` was installed with locked/pinned dependencies.
Its README setup must copy `data/*.csv` into `app/data/` before API tests; skipping that step produces
missing-dataset failures. The corrected documented sequence is tested. That revision contains the older
LPBF/WAAM baseline, not the current uncommitted four-process/Pareto/tutorial candidate.
The baseline passes `37 passed, 8 subtests passed`, eight frontend tests and its production build.
It also emitted a sandbox pytest-cache warning; the tests themselves passed. The current-candidate
run reports the separate counts above. Neither check represents independent teammate acceptance.
Current-candidate tests therefore establish local source behavior; publication and public clean-clone
reproduction remain explicit open gates. No deployment result is inferred here.

A heuristic scan of tracked and non-ignored candidate text found no matching GitHub/OpenAI/AWS
credential patterns, private-key blocks or non-example environment files. This is limited pattern
coverage, not a complete secret audit; final diff/secret review remains part of publication review.
All relative file links in eleven updated documentation files resolve. The H-06 ledger entry and
the four snapshotted deployment files have unchanged hashes relative to this task's starting state.
