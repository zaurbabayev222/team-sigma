# Plan: AeroQual release 1

**DRAFT, pending team review (2026-10-19).** Once approved, change an interface below only after telling
everyone: all four agents build against it. What and why: [`SPEC.md`](../SPEC.md), [`decisions.md`](decisions.md).

**User:** the quality engineer reviewing each tested LPBF titanium build. **Question:** is the process
stable, and can it meet the customer's minimum tensile strength (LSL)?

## Statistics (n coupons per build, k builds; all in `app/qc.py`)
- Per build: mean x̄ᵢ and standard deviation sᵢ (n − 1). Grand mean X̿ = mean of x̄ᵢ; s̄ = mean of sᵢ.
- c4 = √(2/(n−1))·Γ(n/2)/Γ((n−1)/2); A3 = 3/(c4·√n); B4 = 1 + 3·√(1−c4²)/c4; B3 = max(0, 2 − B4).
- X-bar limits X̿ ± A3·s̄; S limits B3·s̄ to B4·s̄. Flag a build if x̄ᵢ is outside or sᵢ > B4·s̄.
- σ_short = s̄/c4; σ_total = std dev of all coupons (n − 1).
- Cpk = (X̿ − LSL)/(3·σ_short); Ppk = (X̿ − LSL)/(3·σ_total). Failure rate = count(uts < LSL)/(n·k).
- Verdict: flagged build → "not assessable: unstable"; k < 25 → "not assessable: too few builds";
  Cpk ≥ 1.33 → "capable"; else "not capable". 25 and 1.33 are arguments.

## Interfaces (fixed once approved)
1. **CSV columns:** `build_id`, `build_date` (YYYY-MM-DD), `uts_mpa`; optional `chamber_oxygen_ppm`,
   `powder_reuse_count`, `laser_power_w`. One row per coupon. Datasets use LSL = 895 MPa (illustrative).
2. **`analyze(df, lsl, min_builds=25, cpk_target=1.33) -> dict`**, generic column names passed in by the
   profile. Keys: `n_builds`, `n_per_build`, `builds` (list of `{build_id, order, mean, s, flagged, reason}`),
   `xbar` and `s_chart` (`{center, lcl, ucl}`), `sigma_short`, `sigma_total`, `cpk`, `ppk`, `n_coupons`,
   `n_failures`, `failure_rate`, `shapiro_p`, `verdict`, `reason`. Bad input raises `ValueError(message)`.
3. **API:** `GET /health`; `GET /datasets`; `GET /analyze?dataset=<name>&lsl=<MPa>`; `POST /analyze`
   (CSV upload + `lsl`). Returns the `analyze` dict plus `profile` and `parameters` (flagged builds' values).
4. **Profile:** `app/profiles/lpbf.py` holds `PROFILE = {name, label, parameters: [{column, label, unit}]}`.

## Tasks, in order
1. **H-03 statistics** (A, ~4 h). Owns `app/qc.py`, `app/requirements.txt`, `tests/`.
   Known answer: SPEC §4 data, LSL 980 → X̿ 1000, s̄ 10, X-bar 980.46–1019.54, S 0–25.68, Cpk 0.591,
   Ppk 0.571, failures 1/12, "not assessable: too few builds". Same data with `min_builds=4` → "not capable".
   Degenerate: constant data → `cpk`/`ppk` None, verdict "not assessable: no variation"; 1 build,
   unequal coupons, blank `uts_mpa` → `ValueError` naming the build or row.
2. **H-02 datasets** (B, ~3 h, parallel with 1). Owns `data/`. Three CSVs, 30 builds × 3 coupons, fixed
   seeds, `data/README.md` codebook. Test: once H-03 lands, each file gives its SPEC §7 verdict.
3. **H-04 API + profile** (C, ~4 h, parallel; fake result until H-03). Owns `app/` except H-03's files.
   Copy `demos/fastapi`. Test: `testme` starts it; curl `/analyze` on a data file = H-03's numbers.
   Degenerate: a bad CSV returns HTTP 400 with the `ValueError` message.
4. **H-08 part 1** (done: the repo is public). **H-06 deploy** (C, ~2 h) right after 3 runs locally.
   Test: workflow green; public URL answers 200 logged out with the same numbers.
5. **H-05 page + demo** (D, ~5 h, parallel; sample JSON until 3). Owns `app/frontend/`, `demo/`.
   Copy `demos/reactfront`; delete its browser-side `spc.js` maths, display only. Test: Playwright shows
   the verdict per dataset; `demo/README.md` walks all three.
6. **H-07 README** (B, ~2 h) then **H-08 part 2** (B): fresh clone passes tests; Devpost submitted.

## Decisions (from H-01, 2026-10-19)
- X-bar and S by build (not I-MR on build means: that hid coupon spread); lower Cpk/Ppk; failure rate.
- LPBF only, with one profile file per process so others plug in later.
- Minimal inputs: 3 required columns + LSL; 3 optional parameters.
- FastAPI + React in plain JavaScript; Python computes every number.

## Biggest risks
1. **A wrong statistic looks right.** The stats-reviewer agent checks H-03 in a fresh session; no PASS, no check-in.
2. **Deploy breaks late.** Deploy the bare API first (step 4), then redeploy as features land.
3. **Datasets missing on the server.** Deploys bundle `app/` only, and `data/` sits outside it. C decides
   in H-04 how the files ship (for example, copied into the bundle by `manifestme`) and tests it live.
