# AeroQual — Critical & High-Priority Application Verification and Fixes

You are working in the `team-sigma` repository as a senior full-stack engineer, manufacturing systems engineer, and Six Sigma quality analyst.

## Mission
Verify and stabilize the **existing AeroQual application** across its implemented additive-manufacturing process profiles and synthetic scenarios. Fix confirmed critical/high-priority defects, preserve statistical integrity, and produce clear test evidence. **Do not create, edit, redesign, or reference any standalone HTML demonstration, executive brief, slide deck, or presentation artifact.** **Posit Connect deployment is out of scope.**

## Operating constraints
1. First inspect the current checked-out branch, working-tree status, latest `origin/main` history, `CONTRACT.yaml`, `SPEC.md`, `PRODUCT.md`, README, task assignments, tests, frontend/backend sources, profiles, and demo data. Report the exact commit SHA. Do not overwrite uncommitted or teammate changes.
2. Respect ownership in `CONTRACT.yaml`. Identify conflicting ownership before editing shared files. Do not modify H-06 deployment assets, credentials, CI/CD deployment workflows, or Posit Connect configuration.
3. Reuse existing modules and APIs. Do not replace the validated Python statistics with browser-side calculations or rewrite functioning architecture merely for style.
4. Verify actual implemented profiles and datasets rather than assuming their counts or names. Clearly distinguish implemented, tested, and planned functionality.
5. Work incrementally: reproduce a failure, implement the smallest robust fix, add a regression test, and rerun affected tests. Do not commit, push, merge, or deploy without explicit approval.

## Critical priority A — End-to-end application integration
- Establish a reliable local Windows PowerShell startup procedure for FastAPI and React/Vite in Positron. Install missing project-local dependencies only if necessary; document commands.
- Verify backend health, profile discovery, dataset discovery, selected-profile analysis, CSV upload, and response schemas against the current frontend's requests. Catch mismatched paths, methods, field names, CORS, error handling, and stale assumptions.
- Exercise every implemented manufacturing profile and every included synthetic scenario. Confirm scenario selection updates all dependent KPIs, charts, tables, labels, units, and verdicts consistently.
- Verify the frontend never silently substitutes a different process, scenario, specification, or synthetic result when an API request fails.
- Test invalid CSVs, missing columns, nonnumeric values, malformed subgroup data, unsupported profiles, missing specifications, and server failures. Errors should be actionable and should not display stale results.
- Verify investigation drill-down, build/coupon traceability, Pareto selections, filters, and any user-facing analysis actions actually work.

## Critical priority B — Statistical correctness and safeguards
- Treat the Python backend as the authoritative calculation engine. Compare its outputs to approved known-answer examples in `SPEC.md` and reproducible datasets; use tolerances stated by the project, not invented acceptance criteria.
- Validate X-bar/S control limits, subgroup assumptions, chronological ordering, flagged-build rules, one-sided Cpk/Ppk, observed failure rate, and handling of zero/undefined variability.
- Preserve safeguards for insufficient sample size, instability, missing tests, incompatible material/process/specification groupings, and non-assessable results. An unstable process must not receive an unconditional capable/incapable verdict.
- Keep **customer specification limits** distinct from **statistical control limits**. Never imply statistical capability equals certification, acceptance of a specific part, or airworthiness.
- Verify Pareto categories, denominator definitions, missingness handling, and that descriptive associations or investigation hints are not presented as causal proof.
- Add or improve focused pytest coverage for every confirmed defect and edge case. Avoid modifying formulas unless a reproducible error is demonstrated.

## High priority C — Browser and UX quality assurance
- Use the configured Playwright MCP to exercise the **existing live React application**, not a standalone presentation.
- Check navigation, selectors, API loading/error states, chart rendering, tooltip legibility, keyboard interaction, tables, filtering, responsive behavior at desktop and mobile widths, and browser console errors.
- Verify users can quickly answer: Is this process stable? Does it appear capable against the selected customer specification? Which builds or process measurements deserve investigation?
- Improve only confirmed high-impact usability defects. Keep concise engineering terminology, clear units, accessible status distinctions, and explicit reasons for withheld conclusions.
- Preserve existing design and teammate-owned frontend work unless coordinated changes are necessary.

## High priority D — Reproducibility and handoff
- Run existing Python and frontend test suites, profile/dataset validators, build checks, and applicable lint/type checks. Record exact commands and pass/fail counts.
- Verify a fresh local setup can start both application services and load the demonstration scenarios without undocumented manual intervention.
- Update **application setup, testing, and troubleshooting documentation only** as needed. Do not edit presentation or deployment documentation.
- Produce a concise final verification matrix: feature/profile/scenario, test method, observed result, status, and remaining risks.

## Execution order
1. **Read-only audit:** inspect repo history, ownership, current code and tests; summarize confirmed gaps and proposed files to touch.
2. **Local baseline:** start existing backend/frontend and run tests; capture failures.
3. **Fix critical issues:** backend/frontend contract, profile/scenario consistency, upload validation, statistical safeguards, and broken drill-downs.
4. **Verify in browser:** Playwright end-to-end checks and responsive/accessibility smoke tests.
5. **Document and report:** rerun tests, provide evidence and local preview commands.

## Required final response
- Exact branch and commit audited; relevant recent commits.
- What already worked, what was broken, and what changed (with file paths).
- Test commands, results, and remaining unverified cases.
- Status by supported printing process and synthetic scenario.
- Exact local PowerShell startup commands and local app URL.
- Any decisions or ownership approvals needed before further changes.

## Hard exclusions
**Do not** create or modify standalone HTML files, briefing templates, executive presentations, slides, presentation scripts, or demo decks. **Do not** change Posit Connect deployment, H-06, CI/CD deployment, secrets, public URLs, or hosting configuration. **Do not** commit, push, merge, or deploy without permission.

Start with the read-only audit and report your proposed changes before editing files that are owned by other contributors.
