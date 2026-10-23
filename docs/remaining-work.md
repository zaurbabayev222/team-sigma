# Remaining work

Status as of 23 October 2026. Technical evidence is in [evaluation.md](evaluation.md); task ownership
stays in [CONTRACT.yaml](../CONTRACT.yaml).

## Done

- **H-06 deploy:** the public app opens logged out, and its numbers match the Python core.
- **H-02 data, H-05 demo:** team members who did not build them checked every documented scenario on
  the live app and got the documented numbers.
- **H-07 README, H-08 reproducibility:** the public repository was cloned into an empty folder and set
  up from the README. The app started, and all Python and frontend tests plus the four data
  validators passed. A key scan found no real credentials.

## Left before the deadline

- **H-08 Devpost:** submit the entry using the links in [submission.md](submission.md), then open the
  submitted page logged out and click every link.

## Possible later work

These are options for a separate scope decision, not remaining hackathon requirements:

- A capability histogram with the LSL drawn on it, next to the Cpk and Ppk values.
- Engineering-validated corrective actions and prospective monitoring against a justified stable baseline.
- Additional SPC rules or statistics selected for a documented decision and sampling design.
- Multiple defects per coupon, severity, defect opportunities and stronger inspection traceability.
- New process profiles backed by a codebook, representative synthetic cases and independent known-answer tests.
- Real manufacturing datasets with appropriate provenance, measurement-system review and validation.

The application currently provides monitoring and investigation support. It does not predict strength from
settings, learn a causal process model, certify hardware or prescribe validated machine adjustments.
