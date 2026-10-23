# Submission draft

Prepared text for review. **Submission has not been confirmed.** Assignments and timing remain open.

## Project

**AeroQual — Titanium Additive Manufacturing Quality Dashboard**

Team: **Sigma Airlines**. Track: **Virtual DL Challenge**.
Prompt: **1 — Industrial Systems, 3D Printing for Aerospace** (see [SPEC](../SPEC.md)).

## Problem and user

A titanium additive manufacturing quality engineer needs to understand failed strength tests and
decide which build records to investigate. AeroQual turns coupon-level tensile-test logs into separate
answers about process stability, lower-specification capability and observed below-specification results.

## What it does

A React dashboard calls a FastAPI backend with one plain Python statistical engine. Users select LPBF,
WAAM, EB-PBF or powder-fed laser DED, choose a synthetic example or upload a CSV, and enter the customer
minimum strength in MPa. Required columns are build ID, build date and measured coupon UTS.

X-bar/S charts show build-level mean and spread signals. Lower Cpk/Ppk and observed coupon failures
support interpretation; unstable or insufficient logs receive a withheld capability conclusion.
Signal and optional primary-defect Pareto views link categories to build/coupon evidence. Inclusive date
windows preserve the full-log baseline. Deterministic investigation guidance suggests records to check.

The process profiles change recorded context without changing the statistical formulas. The prototype
does not predict strength, establish root cause, prescribe validated settings or certify aerospace hardware.

## Demonstration and validation

Sixteen seeded synthetic datasets cover four methods with capable, incapable, unstable and inspection
examples. The original three LPBF datasets meet the rubric's 2–3 example requirement; additional files
demonstrate extensions. Data provenance, units and seeds are in the codebook.

The self-contained HTML walkthrough offers 14 lessons with scenario selection, exact CSV downloads,
chart/Pareto interpretation, captured requirement/date experiments and knowledge checks. All displayed
statistics are captured API outputs, with source hashes and API/core parity checks.

Known-answer, degenerate, API, validation and UI checks are linked in [evaluation.md](evaluation.md).
Independent review and public-candidate reproduction remain to be completed before claiming acceptance.

## Links to select for the final entry

- Repository: [team-sigma](https://github.com/zaurbabayev222/team-sigma). Confirm the final published
  revision contains the intended candidate before submitting it.
- Written demo: [demo/README.md](../demo/README.md).
- Interactive artifact: [demo/slidedeck/index.html](../demo/slidedeck/index.html). Download/open the HTML
  or host it as a static artifact; a repository HTML preview is source code, not an interactive website.
- Public application URL: https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/ (H-06, verified logged out on October 22, 2026).
- Devpost entry: add the selected links and confirm actual submission; no entry URL is invented here.

## Final checks still to do

Review the wording, reproduce the walkthrough independently, publish the reviewed candidate, check its
public links and artifact accessibility, then confirm the Devpost submission. H-06 remains outside this task.
