# AeroQual engineering brief — scoped product context

This file applies only to `demo/aeroqual_brief.html`. It does not replace the application specification.

## Confirmed purpose and audience

The user requested an executive engineering quality-review presentation for aerospace quality engineers,
program management and hackathon judges. It must communicate the titanium-bracket strength-test problem
in 30 seconds and support a 2–3 minute interactive review. The governing product facts are SPEC.md and
the implemented Python API. All demonstrated manufacturing records are synthetic.

## Platform and stack

Web; a self-contained offline HTML artifact generated from repository Python API responses. No new
runtime dependency, service, predictive model or browser-side QC engine. The existing React/FastAPI
application, existing tutorial and demo README remain unchanged.

## Confirmed constraints

Four implemented profiles only: LPBF, WAAM, EB-PBF and powder-fed laser DED. Three main scenarios per
method plus separately identified inspection examples. Withhold capability for unstable input; show
Cpk/Ppk descriptively. Control limits and customer LSL remain distinct. No causal, operating-window,
flightworthiness, release-authority or deployment claim. Snapshot provenance includes exact revision,
source hashes, data hashes and API/core parity. Keyboard, responsive and print support are required.

The user explicitly fixed the replacement aesthetic and flipbook presentation; no wider app rebrand
or product discovery is authorized. Detailed direction is scoped in DESIGN.md.
