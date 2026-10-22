# Remaining work

This is an open-ended handoff, not a set of assigned people or dates. Technical evidence is in
[evaluation.md](evaluation.md); historical task ownership stays in [CONTRACT.yaml](../CONTRACT.yaml).
The user approved committing and pushing the reviewed candidate to main. Independent reproduction of
the published revision and submission confirmation remain separate gates.

## Independent review and release

- Follow the [interactive walkthrough](../demo/slidedeck/index.html) and [written demo](../demo/README.md)
  without assistance from their author. Confirm the displayed numbers and record any confusing steps.
- Explain the known-answer calculation, subgroup assumptions, stability gate, lower-only indices,
  full-log control-limit baseline, and the different Pareto denominators.
- Review the published diff, including statistical tests, synthetic-data provenance and documentation.
  Record any follow-up findings. No independent acceptance is implied by local test success.
- Clone the resulting public revision into an empty folder and follow the README setup and launch steps.
  Confirm the dashboard, all sixteen examples, uploads and tutorial downloads. The local committed-baseline
  clone check does not establish that the latest candidate is reproducible from GitHub.
- Review the [submission draft](submission.md), choose final links/artifacts and confirm the Devpost entry
  is submitted. Do not infer submission from a prepared description or a public repository.

## Existing contract gates

- **H-02:** automated data/codebook checks are available; formal check-in remains with the reviewed commit.
- **H-05:** independent reproduction of the demo remains to be recorded.
- **H-07:** independent fresh-clone walkthrough remains; the public live URL depends on H-06.
- **H-08:** public-revision reproduction, final secret review and Devpost confirmation remain.
- **H-15:** documentation/tutorial checks are complete and checked in with the approved commit; independent
  review remains with H-05/H-07 rather than being implied by this task's completion.

**H-06 is excluded from this update.** Its ledger entry and deployment files are preserved. This document
does not verify a public server, change deployment configuration or claim the current candidate is live.

## Possible later work

These are options for a separate scope decision, not remaining hackathon requirements:

- Engineering-validated corrective actions and prospective monitoring against a justified stable baseline.
- Additional SPC rules or statistics selected for a documented decision and sampling design.
- Multiple defects per coupon, severity, defect opportunities and stronger inspection traceability.
- New process profiles backed by a codebook, representative synthetic cases and independent known-answer tests.
- Real manufacturing datasets with appropriate provenance, measurement-system review and validation.

The application currently provides monitoring and investigation support. It does not predict strength from
settings, learn a causal process model, certify hardware or prescribe validated machine adjustments.
