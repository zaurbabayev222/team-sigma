# Synthetic LPBF build logs — H-02 codebook

**Every measurement in these files is invented for software testing.** No printer, contractor,
laboratory or customer supplied these data. The values, dates, operating settings, and **895 MPa
lower specification limit (LSL)** are illustrative; they are not qualified titanium processing
settings or an aerospace acceptance specification. The LSL is entered separately in the app.

Each CSV contains **30 builds × 3 coupons = 90 coupon rows**, plus a header, with no missing
values. Builds B001–B030 occur in chronological order on September 1–30, 2026. A build's three
coupons share its date and recorded process parameters. Coupon rows are distinguished by their
position within each build; there is no separate coupon-ID column.

## Files and expected behavior

These results were computed with the existing `app/qc.py` function using LSL **895 MPa**,
`min_builds=25`, and `cpk_target=1.33`. Cpk and Ppk are dimensionless, lower-side indices.

| CSV | Behavior | Cpk | Ppk | Coupons below LSL | Flagged builds | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `stable_capable.csv` | Stable reference, strength centered near 950 MPa | 1.683472 | 1.788871 | 0/90 (0%) | 0 | capable |
| `stable_incapable.csv` | Same variation and process logs; every strength reduced by 45 MPa, centered near 905 MPa | 0.311961 | 0.331492 | 17/90 (18.888889%) | 0 | not capable |
| `unstable_shift.csv` | Reference through B019; strength drops by 35 MPa and oxygen rises by 100 ppm from B020 onward | 1.292337 | 0.711731 | 0/90 (0%) | 11 | not assessable |

Interpretation: a stable process can be insufficiently capable; an unstable process cannot receive
a capability verdict even when every observed coupon exceeds the LSL. These CSVs deliberately
separate those behaviors. Control limits are estimated from the data and are not the customer LSL.

The shifted CSV flags **B007, B014, B018, B020, B024, B025, B026, B027, B028, B029, B030**.
The planted change begins at B020, but the current core estimates limits from the **entire log**.
The changed grand mean therefore also flags some earlier builds and does not flag every changed
build. This is expected behavior of the specified implementation, not evidence that the simulated
change began early. A future fixed-baseline method would need a separate design decision. Oxygen
and strength are changed together by construction; this does not establish a causal relationship.

## Column dictionary

| Column | Type and units | Meaning | Real collection source |
| --- | --- | --- | --- |
| `build_id` | Text, no units | Printer build/job identifier, B001–B030; three consecutive rows per build | Build traveler or printer job log, linked to the tensile specimen IDs |
| `build_date` | Date, `YYYY-MM-DD` | Build date used to order the analysis; one date per build | Printer completion timestamp converted to a consistently defined local date |
| `uts_mpa` | Decimal number, MPa | Individual coupon ultimate tensile strength; one result per row | Calibrated tensile-test report: maximum tensile load divided by original specimen cross-sectional area |
| `chamber_oxygen_ppm` | Decimal number, ppm | One illustrative chamber oxygen reading per build, repeated across its coupons | Calibrated printer oxygen sensor log, summarized over an explicitly agreed build interval |
| `powder_reuse_count` | Nonnegative integer, reuse cycles | Number of powder reuse cycles assigned to the build, repeated across coupons | Powder lot/recycling records linked to the build traveler |
| `laser_power_w` | Decimal number, W | Illustrative recorded laser-power setting, repeated across coupons | Printer job recipe/settings log; distinguish commanded power from independently measured power |

The first three columns are required by the app. The last three are optional process context;
the statistics function does not read them. None of these fixtures contains nulls. Missing strength,
unequal coupon counts, one build, and zero variation are exercised in memory by `validate.py`
rather than adding invalid rows to the three demonstration files.

For real collection, use unique coupon identifiers in the source records and join them to their
build and powder lot. Define coupon orientation, specimen geometry, heat treatment, test method,
sensor aggregation interval, and equipment calibration before comparing builds. Obtain the LSL
from the actual customer specification. Preserve timestamps and traceability; do not reuse these
synthetic dates or assume the illustrative operating settings are valid production limits.

## How the files are generated

`generate.py` uses Python's standard-library `random.Random` with fixed seeds **5300** for
strength and **5301** for process context. It draws 90 independent reference strengths from a
normal distribution with mean 950 MPa and standard deviation 10 MPa, then rounds to 0.001 MPa.
There is no seed search, resampling, or filtering inside the generator. The frozen seed was
checked against the core to confirm that it gives the intended demonstration outcomes.

For each build, oxygen is drawn from Normal(40 ppm, 3 ppm), laser power from Normal(200 W, 2 W),
and powder reuse follows `(build_index - 1) % 6`. Oxygen and power are rounded to 0.001 of their
units. Every scenario shares these process readings and reference strength noise. The incapable
case applies the constant −45 MPa offset. The unstable case applies −35 MPa to strength and +100
ppm to oxygen for all coupons in B020–B030. The shifted full log is a mixture of two means; it is
not intended to satisfy a stable normal-process assumption.

## Reproduce and validate

From the repository root:

```bash
python3 data/generate.py --check  # compare CSV bytes with seeded generation, no writes
python data/validate.py          # needs app/requirements.txt installed
python demo/check.py             # H-05 scenario checks using these CSVs
```

To intentionally regenerate the three CSVs, run `python3 data/generate.py`. That overwrites these
three named files only. Use the pinned Python environment from `app/requirements.txt` for analysis;
the generator itself requires only Python's standard library. Review any output differences before
changing the frozen expected values in `validate.py` or this codebook.

The validator checks reproducible bytes, schema, finite values, valid ordered dates, 30 equal-size
builds, within-build parameter consistency, the precise planted shifts, frozen outcome numbers and
flag lists. It also checks that zero variation returns undefined capability and that one build,
unequal coupons or missing strength raise clear errors. The independent SPEC known-answer test
and other statistic tests remain in `tests/`; this task does not change the statistics implementation.
