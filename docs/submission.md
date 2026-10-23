# Submission text

Text and links for the Devpost entry. The app, the demo and a fresh public clone were checked on October 23, 2026.

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
The team reproduced the demo on the live app, and a fresh clone of the public repo passed every check (October 23, 2026).

## Links to select for the final entry

- Repository: [team-sigma](https://github.com/zaurbabayev222/team-sigma).
- Demo site (start here): https://zaurbabayev222.github.io/team-sigma/demo/
- Written demo: [demo/README.md](../demo/README.md).
- Interactive tutorial: https://zaurbabayev222.github.io/team-sigma/demo/slidedeck/ (source:
  [demo/slidedeck/index.html](../demo/slidedeck/index.html)).
- Public application URL: https://connect.systems-apps.com/content/0639302d-988d-4820-961e-e3268e78b0b0/ (H-06, verified logged out on October 22, 2026).
- Devpost entry: add the selected links and confirm actual submission; no entry URL is invented here.

## Final step

Submit the Devpost entry with the links above, then open the submitted page logged out and click every link.
