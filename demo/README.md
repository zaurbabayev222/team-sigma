# AeroQual demonstration

All examples are synthetic LPBF titanium coupon data. The illustrative lower strength limit is **895 MPa**, not a certified titanium requirement. Python calculates every QC statistic; the dashboard displays its response. See [the data codebook](../data/README.md) for provenance, units and seeded generation.

## Verification status

The datasets and API are now present. All three examples below were selected and analyzed in the running local AeroQual dashboard, with LSL **895 MPa**, a minimum of **25 builds** and Cpk target **1.33**. The tables record the numbers as displayed, including the dashboard's rounding. Each file contains **30 builds × 3 coupons = 90 coupons**, ordered B001–B030.

[results.json](results.json) captures the full-precision Python core results for all three datasets. The displayed outputs below were checked against those results. Independent teammate reproduction is still required before H-05 is formally complete; local verification is not evidence of a public deployment.

## Start and reproduce

From the repository root, with Python 3.12 and Node/npm available:

```bash
source /tmp/aeroqual-venv/bin/activate  # or activate your own Python 3.12 environment
python -m pip install -r app/requirements.txt
bash app/testme.sh
```

Keep that terminal running. The startup script syncs the example datasets and builds the dashboard. Open [AeroQual locally](http://127.0.0.1:8000/dashboard/). Select **stable_capable**, **stable_incapable** or **unstable_shift** in **Example dataset**, leave **Minimum strength, LSL (MPa)** at **895**, and click **Analyze builds**. Alternatively upload the corresponding CSV from `data/`; clear the upload before switching back to examples.

In another terminal, compare all core values with the running API and optionally refresh the full-precision capture:

```bash
/tmp/aeroqual-venv/bin/python demo/check.py --base-url http://127.0.0.1:8000 --output demo/results.json
```

If `AEROQUAL_VENV` was set when starting the app, use that environment's Python instead. To check the three datasets without starting the API:

```bash
/tmp/aeroqual-venv/bin/python demo/check.py --output demo/results.json
```

The API check compares every core value, chart limit, build flag and reason, rather than only the rounded summary. A successful run ends with `PASS: all three synthetic scenarios and API parity.` A core-only run explicitly says API/browser reproduction is still required. No credentials are needed for local testing.

## Observed summary

Cpk and Ppk are dimensionless lower-side indices. Sigma and chart limits are in MPa.

| Displayed output | `stable_capable.csv` | `stable_incapable.csv` | `unstable_shift.csv` |
| --- | ---: | ---: | ---: |
| Verdict | **capable** | **not capable** | **not assessable** |
| Cpk (lower) | 1.683 | 0.312 | 1.292 |
| Ppk (lower) | 1.789 | 0.331 | 0.712 |
| Failure rate | 0.0% (0/90) | 18.9% (17/90) | 0.0% (0/90) |
| Builds / coupons per build | 30 / 3 | 30 / 3 | 30 / 3 |
| Flagged builds | None | None | 11 (listed below) |
| Within-build sigma | 10.937 | 10.937 | 10.937 |
| Overall sigma | 10.292 | 10.292 | 19.859 |
| Shapiro–Wilk p-value | 0.8058 | 0.8058 | 0.0304 |

### Stable, capable

```bash
curl --fail 'http://127.0.0.1:8000/analyze?dataset=stable_capable&lsl=895'
```

Displayed reason: **“Cpk 1.68 is at or above the target 1.33.”** Both charts show no flagged builds, and no coupons are below the minimum.

**How to read this:** the stable synthetic process has enough distance above the customer minimum to meet the configured capability target.

### Stable, not capable

```bash
curl --fail 'http://127.0.0.1:8000/analyze?dataset=stable_incapable&lsl=895'
```

Displayed reason: **“Cpk 0.31 is below the target 1.33.”** Both charts show no flagged builds, but 17 of 90 coupons fall below the minimum.

**How to read this:** a process can be stable while consistently operating too close to the required minimum strength.

### Unstable shift

```bash
curl --fail 'http://127.0.0.1:8000/analyze?dataset=unstable_shift&lsl=895'
```

Displayed reason: **“Not assessable: process is unstable, builds out of control: B007, B014, B018, B020, B024, B025, B026, B027, B028, B029, B030.”**

**How to read this:** investigate the process change before interpreting capability. All 90 observed coupons exceed the LSL, but that does not establish capability for an unstable process. The lower Ppk and larger overall sigma reflect variation across the shifted log.

## Observed chart limits

| Dataset | X-bar LCL | X-bar center | X-bar UCL | S LCL | S center | S UCL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `stable_capable.csv` | 931.292 | 950.236 | 969.179 | 0.000 | 9.693 | 24.892 |
| `stable_incapable.csv` | 886.292 | 905.236 | 924.179 | 0.000 | 9.693 | 24.892 |
| `unstable_shift.csv` | 918.459 | 937.402 | 956.345 | 0.000 | 9.693 | 24.892 |

X-bar monitors build means; S monitors within-build coupon spread. These statistical control limits are distinct from the customer LSL. Red points identify flagged builds; hover for the build ID, value and reason. A red build does not necessarily contain a failed coupon. Failures count coupons strictly below the LSL; a coupon equal to the LSL passes.

### Unstable example: flagged-build table

The stable examples display **“No builds flagged.”** The unstable example displays:

| Build | Date | Mean (MPa) | S (MPa) | Reason |
| --- | --- | ---: | ---: | --- |
| B007 | 2026-09-07 | 957.829 | 15.587 | mean above the X-bar upper limit |
| B014 | 2026-09-14 | 958.102 | 8.849 | mean above the X-bar upper limit |
| B018 | 2026-09-18 | 958.538 | 5.698 | mean above the X-bar upper limit |
| B020 | 2026-09-20 | 905.011 | 11.863 | mean below the X-bar lower limit |
| B024 | 2026-09-24 | 910.522 | 11.349 | mean below the X-bar lower limit |
| B025 | 2026-09-25 | 917.185 | 8.800 | mean below the X-bar lower limit |
| B026 | 2026-09-26 | 916.068 | 5.110 | mean below the X-bar lower limit |
| B027 | 2026-09-27 | 912.733 | 14.734 | mean below the X-bar lower limit |
| B028 | 2026-09-28 | 909.991 | 8.653 | mean below the X-bar lower limit |
| B029 | 2026-09-29 | 916.520 | 3.727 | mean below the X-bar lower limit |
| B030 | 2026-09-30 | 917.534 | 9.460 | mean below the X-bar lower limit |

The simulated strength drop and oxygen rise begin at **B020**. The current core estimates limits from the entire log, so the shifted grand mean also flags B007, B014 and B018 and does not flag every build after the change. Do not interpret those earlier flags as evidence that the planted change began earlier. All listed flags concern the build mean; none exceeds the S upper limit.

## Observed strength distribution

Each entry shows the displayed strength interval in MPa and its coupon count. These are rounded histogram boundaries, not specification thresholds; failures are determined from the original coupon strengths.

| Bin | Stable capable: interval / count | Stable incapable: interval / count | Unstable shift: interval / count |
| --- | --- | --- | --- |
| 1 | 927.302–933.577 / 3 | 882.302–888.577 / 3 | 895.238–905.521 / 6 |
| 2 | 933.577–939.852 / 14 | 888.577–894.852 / 14 | 905.521–915.805 / 11 |
| 3 | 939.852–946.128 / 13 | 894.852–901.128 / 13 | 915.805–926.088 / 12 |
| 4 | 946.128–952.403 / 21 | 901.128–907.403 / 21 | 926.088–936.371 / 9 |
| 5 | 952.403–958.678 / 22 | 907.403–913.678 / 22 | 936.371–946.654 / 15 |
| 6 | 958.678–964.954 / 10 | 913.678–919.954 / 10 | 946.654–956.938 / 20 |
| 7 | 964.954–971.229 / 5 | 919.954–926.229 / 5 | 956.938–967.221 / 13 |
| 8 | 971.229–977.504 / 2 | 926.229–932.504 / 2 | 967.221–977.504 / 4 |

Each distribution totals 90 coupons. The displayed Shapiro–Wilk p-value is 0.8058 in both stable examples and 0.0304 in the shifted example. A small p-value raises concern about normality; a large value does not prove it. Capability also requires stability and equal-size, time-ordered subgroups.

## Observed process parameters

The page's **“Usual range”** is the observed minimum–maximum among **unflagged builds**. It is not a qualified operating range. Because some changed builds remain unflagged, the unstable example's oxygen reference range includes elevated values.

| Parameter | Stable capable | Stable incapable | Unstable shift |
| --- | --- | --- | --- |
| Chamber oxygen (ppm) | 33.167–47.072 | 33.167–47.072 | 34.454–141.447 |
| Powder reuse (times) | 0.000–5.000 | 0.000–5.000 | 0.000–5.000 |
| Laser power (W) | 195.817–204.250 | 195.817–204.250 | 195.817–204.250 |

The stable examples have no flagged-build parameter rows. The unstable example displays these recorded values:

| Flagged build | Chamber oxygen (ppm) | Powder reuse (times) | Laser power (W) |
| --- | ---: | ---: | ---: |
| B007 | 38.774 | 0.000 | 199.215 |
| B014 | 46.303 | 1.000 | 199.883 |
| B018 | 33.167 | 5.000 | 198.842 |
| B020 | 141.926 | 1.000 | 200.804 |
| B024 | 138.497 | 5.000 | 202.561 |
| B025 | 143.933 | 0.000 | 199.948 |
| B026 | 137.093 | 1.000 | 198.500 |
| B027 | 140.228 | 2.000 | 198.736 |
| B028 | 147.072 | 3.000 | 198.026 |
| B029 | 142.306 | 4.000 | 198.831 |
| B030 | 136.907 | 5.000 | 200.894 |

Oxygen and strength were changed together by the synthetic generator. The comparison suggests where to investigate, but does not establish causation. The tool supports quality-engineering decisions and does not certify parts.

## Independent teammate reproduction

A teammate who did not write the demo must follow the commands above and record the date, commit or local revision, checker terminal output, and whether the dashboard matches all three cases. That independent human reproduction has not yet been recorded. The observations here are agent verification, not a substitute for that requirement.

## Frontend development checks

```bash
npm --prefix app/frontend ci --cache /tmp/aeroqual-npm-cache
npm --prefix app/frontend test
npm --prefix app/frontend run build
```

Frontend tests use labeled fixtures and mocked HTTP responses to check rendering and API wiring. For the statistics and real HTTP API tests:

```bash
/tmp/aeroqual-venv/bin/python -m pytest tests
```
