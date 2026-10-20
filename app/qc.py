"""Core QC statistics: X-bar and S chart by build, Cpk, Ppk, failure rate.

One plain function, `analyze`. No web code and no plotting here.
Column names are passed in, so this file knows nothing about any one process.

Method (SPEC.md section 4):
  - Each subgroup (a "build") has n coupons. Per build: mean and std dev (ddof=1).
  - X-double-bar = mean of build means; s-bar = mean of build std devs.
  - X-bar limits: X-double-bar +/- A3 * s-bar.  S limits: B3 * s-bar to B4 * s-bar.
  - sigma_short = s-bar / c4 (within-build).  sigma_total = std dev of all values.
  - Cpk = (X-double-bar - LSL) / (3 * sigma_short)  (lower side only).
  - Ppk = (X-double-bar - LSL) / (3 * sigma_total).
Assumptions: values roughly normal, builds in time order, equal coupons per build,
only a lower spec limit.
"""
import math

import pandas as pd
from scipy import stats


def c4_constant(n):
    """c4 = sqrt(2/(n-1)) * Gamma(n/2) / Gamma((n-1)/2), computed from n."""
    return math.sqrt(2 / (n - 1)) * math.gamma(n / 2) / math.gamma((n - 1) / 2)


def chart_constants(n):
    """Return c4, A3, B3, B4 for subgroup size n."""
    c4 = c4_constant(n)
    spread = 3 * math.sqrt(1 - c4**2) / c4
    return {
        "c4": c4,
        "A3": 3 / (c4 * math.sqrt(n)),
        "B3": max(0.0, 1 - spread),  # a standard deviation cannot be negative
        "B4": 1 + spread,
    }


def analyze(df, lsl, subgroup_col="subgroup", order_col="order", value_col="value",
            min_builds=25, cpk_target=1.33):
    """Analyze one table of coupons (one row each) against a lower spec limit `lsl`.

    Returns a dict with keys: n_builds, n_per_build, builds, xbar, s_chart,
    sigma_short, sigma_total, cpk, ppk, n_coupons, n_failures, failure_rate,
    shapiro_p, verdict, reason. Each entry of `builds` is
    {build_id, order, mean, s, flagged, reason}.

    verdict is one of "capable", "not capable", "not assessable". `reason` is a
    sentence; when the verdict is "not assessable" it contains exactly one of:
      "no variation"    (all coupons equal, Cpk and Ppk are None)
      "unstable"        (at least one build is flagged)
      "too few builds"  (fewer than min_builds builds)

    Raises ValueError for bad input (missing column, blank value, fewer than 2
    builds, unequal or fewer than 2 coupons per build, lsl not a finite number).
    """
    # ---- check the input ----
    if isinstance(lsl, bool) or not isinstance(lsl, (int, float)) or not math.isfinite(lsl):
        raise ValueError(f"lsl must be a finite number, got {lsl!r}")
    for col in (subgroup_col, order_col, value_col):
        if col not in df.columns:
            raise ValueError(f"missing column '{col}'")
    values = pd.to_numeric(df[value_col], errors="coerce")
    bad = df.index[values.isna() | values.isin([math.inf, -math.inf])]
    if len(bad) > 0:
        raise ValueError(f"blank or non-numeric '{value_col}' at row {bad[0]}")
    data = pd.DataFrame({
        "build": df[subgroup_col].astype(str),
        "order": df[order_col].astype(str),
        "value": values.astype(float),
    })

    sizes = data.groupby("build", sort=False).size()
    if len(sizes) < 2:
        raise ValueError("need at least 2 builds")
    n = int(sizes.iloc[0])
    for name, size in sizes.items():
        if size != n:
            raise ValueError(f"build '{name}' has {size} coupons but the first build has {n}")
    if n < 2:
        raise ValueError("need at least 2 coupons per build")

    # ---- per-build mean and s, in time order ----
    per = data.groupby("build", sort=False).agg(
        order=("order", "first"), mean=("value", "mean"), s=("value", "std"))  # std is ddof=1
    per = per.sort_values("order", kind="stable")

    # ---- chart limits ----
    const = chart_constants(n)
    grand_mean = float(per["mean"].mean())
    s_bar = float(per["s"].mean())
    xbar = {"center": grand_mean, "lcl": grand_mean - const["A3"] * s_bar,
            "ucl": grand_mean + const["A3"] * s_bar}
    s_chart = {"center": s_bar, "lcl": const["B3"] * s_bar, "ucl": const["B4"] * s_bar}

    # ---- flag builds ----
    builds = []
    for name, row in per.iterrows():
        reasons = []
        if row["mean"] < xbar["lcl"]:
            reasons.append("mean below the X-bar lower limit")
        if row["mean"] > xbar["ucl"]:
            reasons.append("mean above the X-bar upper limit")
        if row["s"] > s_chart["ucl"]:
            reasons.append("s above the S chart upper limit")
        builds.append({"build_id": str(name), "order": str(row["order"]),
                       "mean": float(row["mean"]), "s": float(row["s"]),
                       "flagged": bool(reasons), "reason": "; ".join(reasons)})

    # ---- capability (None when sigma is 0: never inf) ----
    sigma_short = s_bar / const["c4"]
    sigma_total = float(data["value"].std(ddof=1))
    cpk = None if sigma_short == 0 else (grand_mean - lsl) / (3 * sigma_short)
    ppk = None if sigma_total == 0 else (grand_mean - lsl) / (3 * sigma_total)

    # ---- failures and normality ----
    n_coupons = len(data)
    n_failures = int((data["value"] < lsl).sum())  # equal to the LSL passes
    shapiro_p = None
    if n_coupons >= 3 and sigma_total > 0:
        shapiro_p = float(stats.shapiro(data["value"]).pvalue)

    # ---- verdict, checked in this order ----
    flagged = [b["build_id"] for b in builds if b["flagged"]]
    if cpk is None or ppk is None:
        verdict = "not assessable"
        reason = "Not assessable: no variation in the data, so Cpk and Ppk are undefined."
    elif flagged:
        verdict = "not assessable"
        reason = "Not assessable: process is unstable, builds out of control: " + ", ".join(flagged) + "."
    elif len(builds) < min_builds:
        verdict = "not assessable"
        reason = f"Not assessable: too few builds ({len(builds)} given, {min_builds} needed)."
    elif cpk >= cpk_target:
        verdict = "capable"
        reason = f"Cpk {cpk:.2f} is at or above the target {cpk_target}."
    else:
        verdict = "not capable"
        reason = f"Cpk {cpk:.2f} is below the target {cpk_target}."

    return {
        "n_builds": len(builds), "n_per_build": n, "builds": builds,
        "xbar": xbar, "s_chart": s_chart,
        "sigma_short": float(sigma_short), "sigma_total": sigma_total,
        "cpk": None if cpk is None else float(cpk),
        "ppk": None if ppk is None else float(ppk),
        "n_coupons": n_coupons, "n_failures": n_failures,
        "failure_rate": n_failures / n_coupons,
        "shapiro_p": shapiro_p, "verdict": verdict, "reason": reason,
    }
