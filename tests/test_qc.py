"""Tests for app/qc.py. The known answer comes from SPEC.md section 4."""
import json
import math

import pandas as pd
import pytest

from app.qc import analyze, c4_constant, chart_constants


def make_df(builds):
    """builds: dict of name -> list of values. Orders are 2026-01-01, 02, ..."""
    rows = []
    for i, (name, values) in enumerate(builds.items(), start=1):
        for v in values:
            rows.append({"subgroup": name, "order": f"2026-01-{i:02d}", "value": v})
    return pd.DataFrame(rows)


KNOWN = {
    "B1": [990, 1000, 1010],
    "B2": [1005, 1010, 1015],
    "B3": [975, 990, 1005],
    "B4": [990, 1000, 1010],
}


def test_known_answer_spec_section_4():
    r = analyze(make_df(KNOWN), lsl=980)
    assert r["n_builds"] == 4 and r["n_per_build"] == 3
    assert r["xbar"]["center"] == pytest.approx(1000)
    assert r["xbar"]["lcl"] == pytest.approx(980.46, abs=0.01)
    assert r["xbar"]["ucl"] == pytest.approx(1019.54, abs=0.01)
    assert r["s_chart"]["center"] == pytest.approx(10)
    assert r["s_chart"]["lcl"] == 0
    assert r["s_chart"]["ucl"] == pytest.approx(25.68, abs=0.01)
    assert r["sigma_short"] == pytest.approx(11.284, abs=0.001)
    assert r["sigma_total"] == pytest.approx(11.677, abs=0.001)
    assert r["cpk"] == pytest.approx(0.591, abs=0.001)
    assert r["ppk"] == pytest.approx(0.571, abs=0.001)
    assert r["n_coupons"] == 12 and r["n_failures"] == 1
    assert r["failure_rate"] == pytest.approx(1 / 12)
    assert not any(b["flagged"] for b in r["builds"])
    assert [b["build_id"] for b in r["builds"]] == ["B1", "B2", "B3", "B4"]
    assert r["builds"][1]["mean"] == pytest.approx(1010)
    assert r["builds"][1]["s"] == pytest.approx(5)
    assert r["verdict"] == "not assessable"
    assert "too few builds" in r["reason"]


def test_min_builds_4_gives_not_capable():
    r = analyze(make_df(KNOWN), lsl=980, min_builds=4)
    assert r["verdict"] == "not capable"


def test_capable_when_cpk_high():
    r = analyze(make_df(KNOWN), lsl=900, min_builds=4)
    assert r["verdict"] == "capable"


def test_value_equal_to_lsl_passes():
    r = analyze(make_df(KNOWN), lsl=975)
    assert r["n_failures"] == 0


def test_constant_data_is_not_assessable():
    r = analyze(make_df({"A": [1000] * 3, "B": [1000] * 3, "C": [1000] * 3}), lsl=980)
    assert r["cpk"] is None and r["ppk"] is None
    assert r["verdict"] == "not assessable"
    assert "no variation" in r["reason"]
    assert r["shapiro_p"] is None
    assert "inf" not in json.dumps(r).lower()


def test_one_build_raises():
    with pytest.raises(ValueError, match="at least 2 builds"):
        analyze(make_df({"A": [1, 2, 3]}), lsl=0)


def test_unequal_coupons_names_the_build():
    with pytest.raises(ValueError, match="B2"):
        analyze(make_df({"B1": [1, 2, 3], "B2": [1, 2, 3, 4]}), lsl=0)


def test_nan_value_names_the_row():
    df = make_df(KNOWN)
    df.loc[5, "value"] = float("nan")
    with pytest.raises(ValueError, match="row 5"):
        analyze(df, lsl=980)


def test_missing_column_and_bad_lsl():
    with pytest.raises(ValueError, match="missing column"):
        analyze(make_df(KNOWN).drop(columns="value"), lsl=980)
    with pytest.raises(ValueError, match="lsl"):
        analyze(make_df(KNOWN), lsl=float("nan"))


def test_one_coupon_per_build_raises():
    with pytest.raises(ValueError, match="at least 2 coupons"):
        analyze(make_df({"A": [1], "B": [2]}), lsl=0)


def test_planted_shift_is_flagged():
    # 12 builds that wobble around 1000 with within-build spread near 10,
    # then build B7 is shifted up by 60 MPa.
    offsets = [-4, 3, 0, 5, -2, 1, 0, -3, 4, 2, -1, 0]
    builds = {f"B{i}": [1000 + offsets[i] - 10, 1000 + offsets[i], 1000 + offsets[i] + 10]
              for i in range(12)}
    builds["B7"] = [v + 60 for v in builds["B7"]]
    r = analyze(make_df(builds), lsl=950)
    flagged = [b["build_id"] for b in r["builds"] if b["flagged"]]
    assert flagged == ["B7"]
    assert r["verdict"] == "not assessable"
    assert "unstable" in r["reason"]


def test_constants_for_n_3():
    c = chart_constants(3)
    assert c4_constant(3) == pytest.approx(0.8862, abs=0.0001)
    assert c["A3"] == pytest.approx(1.954, abs=0.001)
    assert c["B4"] == pytest.approx(2.568, abs=0.001)
    assert c["B3"] == 0


def test_sorted_by_order_column():
    df = make_df(KNOWN).iloc[::-1].reset_index(drop=True)  # reverse the rows
    r = analyze(df, lsl=980)
    assert [b["build_id"] for b in r["builds"]] == ["B1", "B2", "B3", "B4"]


def test_json_serialisable():
    r = analyze(make_df(KNOWN), lsl=980)
    json.dumps(r)
    assert math.isfinite(r["cpk"])
