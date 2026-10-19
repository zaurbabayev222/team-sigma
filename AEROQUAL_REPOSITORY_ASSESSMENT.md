# AeroQual — Repository Assessment and Implementation Plan

**Project:** Cornell SYSEN 5300 Six Sigma Hackathon  
**Repository:** `zaurbabayev222/team-sigma`  
**Status:** Pre-implementation assessment  
**Scope:** Technology-agnostic titanium additive manufacturing quality dashboard; LPBF is an illustrative demo profile only.

> **Assessment status:** This document records the Codex repository assessment shared by the team. It is a planning document, not evidence that AeroQual functionality has been implemented or deployed.

## Executive summary

AeroQual has a defined product direction and useful starter infrastructure, but **the AeroQual application has not yet been implemented**. The recommended next step is to finalize the MVP specification and team ownership under **H-01** before adding application code.

The proposed architecture is **React/Vite/TypeScript → FastAPI → independent Python statistical engine**. The MVP should prioritize statistically defensible stability, capability, conformance, and build investigation rather than predictive features or extensive design polish.

## 1. Existing repository assets

| Asset | Current state |
|---|---|
| `PRODUCT.md` | Product context, process-neutral scope, statistical safeguards, design principles; reported as untracked at assessment time |
| `PROJECT_OVERVIEW.md` | Project goals, dashboard modules, and synthetic scenario descriptions |
| FastAPI starter | Root, echo, and sum endpoints; CORS; local-run and deployment scripts |
| React/Vite starter | Measurement entry, SVG individuals chart, browser-side I-MR calculations, example tests |
| Supporting infrastructure | Posit Connect workflow templates, agent tooling, pytest configuration |

These are **starter assets**, not integrated AeroQual features.

## 2. Remaining work

- Process-neutral observation schemas and printing-method profile registry.
- CSV validation, specification configuration, units, and specification provenance.
- Three reproducible synthetic scenarios and data dictionary.
- Validated Python SPC, one-sided capability, conformance, and missing-test handling.
- FastAPI analysis endpoints and end-to-end integration.
- React dashboard modules and interactive build investigations.
- Integration tests, Windows setup, documentation, and verified deployment.

At assessment time, there was no AeroQual-specific `app/`, project `tests/`, `data/`, `demo/`, implementation plan, or active deployment workflow.

## 3. Proposed technical architecture

```text
Manufacturing / test CSV data
          |
          v
Process-neutral schemas + method profiles
          |
          v
Python statistical engine (app/qc.py)
          |
          v
FastAPI endpoints
          |
          v
React + Vite + TypeScript dashboard
          |
          v
Overview | SPC & Capability | Relationships | Build Investigation
```

**Engineering rules:**

- Keep statistical calculations authoritative in Python; React should present results, not independently calculate competing statistics.
- Preserve build/coupon grouping, material lot, machine, units, test method, and specification provenance.
- Do not pool incompatible manufacturing processes, heat-treatment conditions, or specification populations.
- Clearly distinguish customer specification limits from statistically calculated control limits.
- Withhold capability conclusions when stability or sample adequacy cannot be established, and explain why.
- LPBF-specific measurements belong in an **optional LPBF demonstration profile**, not in the universal schema.
- A combined Posit Connect deployment may be feasible, but the actual deployment approach must be tested; existing templates deploy frontend and backend separately.

## 4. Open decisions and risks

| Finding | Proposed resolution |
|---|---|
| SPEC has unresolved users, inputs, methods, stack, and known-answer test fields | Finalize in H-01 with its assigned owner, Zaur Babayev |
| React starter calculates I-MR statistics in the browser | Move authoritative statistics to Python |
| React starter uses JavaScript and SVG | Confirm TypeScript and Recharts before implementation |
| Documentation offers alternative delivery modes | Explicitly select React dashboard + FastAPI backend in SPEC |
| Schema/profile ownership and file paths are unclear | Agree on file layout and task owners before coding |
| Starters lack correlated coupon, one-sided specification, and missing-test handling | Make these mandatory statistical acceptance cases |
| Local scripts use Bash; deployment templates are inactive | Add verified Windows/PowerShell instructions and prove deployment early |

Regression, ANOVA, full FMEA, predictive machine learning, and comprehensive support for every AM process are **later-phase enhancements**, not MVP blockers.

## 5. Recommended MVP definition (proposed; pending H-01 approval)

### Primary engineering decision

Determine whether a defined titanium additive manufacturing process is **statistically stable** and **capable of meeting customer-defined tensile strength requirements**, and surface process or quality deviations for investigation.

### Minimum data contract

Each coupon or part test observation should be linked to:

- Build ID, coupon/part ID, machine ID, manufacturing method, timestamp.
- Material lot, post-processing/heat-treatment condition, test orientation, test method.
- Measured tensile strength and any relevant defect/inspection measurements.
- Applicable specification identifier, limit values, units, and provenance.
- Optional process-specific sensor and machine settings supplied through a method profile.

### Initial statistical methods

1. **I-MR statistical process control:** sequential observations, moving ranges, computed control limits, and special-cause flags.
2. **One-sided process capability:** `Cpl` for lower-bounded strength requirements, with a justified within-process variation estimate and explicit stability/data-adequacy checks.
3. **Conformance:** coupon-level strength acceptance and build-level status, with clear denominators and missing-test rules.
4. **First-pass yield:** defined at the chosen unit of analysis; do not confuse tested coupons with accepted builds.

### Demonstration scenarios

| Scenario | Intended behavior |
|---|---|
| Stable and capable | Statistically controlled with sufficient capability against the illustrative specification |
| Stable but incapable | Controlled process with inadequate capability |
| Unstable | Detectable process shift or special cause; capability conclusion withheld |

All demonstration data and thresholds must be clearly labeled **synthetic / illustrative**, not qualified aerospace acceptance criteria.

### MVP dashboard views

- **Overview:** build status, yield, strength failures, and process alerts.
- **Stability & capability:** I-MR charts, strength distribution, specifications, and appropriate capability results or withholding reasons.
- **Build investigation:** process deviations, test results, traceability, and investigation hypotheses.
- **Exploratory relationships:** add only after core statistics and integration are validated.

## 6. Implementation sequence

| Order | Task | Outcome |
|---|---|---|
| 1 | **H-01** — Finalize SPEC, scope, and ownership | Approved engineering decision, schema, methods, stack, and known-answer criteria |
| 2 | Data contract and LPBF demo profile | Technology-neutral schema with one illustrative process profile |
| 3 | **H-02** — Synthetic datasets and codebook | Three deterministic scenarios with documented assumptions |
| 4 | **H-03** — Statistical engine and tests | Validated SPC, one-sided capability, conformance, edge cases |
| 5 | **H-04** — FastAPI integration | End-to-end dataset-to-analysis request |
| 6 | **H-06** — Early deployment proof | Minimal working interface deployed and verified |
| 7 | **H-04/H-05** — Dashboard implementation | Overview, stability/capability, build investigation; exploratory analysis afterward |
| 8 | **H-07/H-08** — Documentation and submission | Reproducibility checks, demo, deployment, submission artifacts |

## 7. Immediate next action: H-01 review

**Assigned owner reported by repository assessment:** Zaur Babayev.

Prepare an H-01 proposal for owner review covering:

1. Primary engineering decision and intended users.
2. Minimum observation schema and units of analysis.
3. Process-neutral core and LPBF demo profile.
4. SPC, one-sided capability, yield, and conformance definitions.
5. Three synthetic scenarios and known-answer test expectations.
6. React/TypeScript + FastAPI stack and deployment topology.
7. MVP boundaries, ownership, and file locations.

**Do not modify the shared SPEC or task ledger without coordinating with its owner.** Once H-01 is approved, begin implementation with the validated data contract and statistical engine.

---

*Source: Codex repository assessment shared in the project discussion. This document organizes that assessment and adds a clearly labeled proposed MVP specification for team review.*
