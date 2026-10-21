"""Tests for the API in app/app.py. The known answer comes from SPEC.md section 4."""
import io
import os

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.qc import analyze

client = TestClient(app)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "spec_example.csv")


def post_csv(text, **fields):
    """POST a CSV given as text; fields are the form values (lsl etc.)."""
    files = {"file": ("test.csv", io.BytesIO(text.encode()), "text/csv")}
    return client.post("/analyze", files=files, data=fields)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_datasets_is_a_list():
    assert isinstance(client.get("/datasets").json()["datasets"], list)


def test_known_answer_and_matches_analyze_directly():
    with open(FIXTURE, "rb") as f:
        response = client.post("/analyze", files={"file": f}, data={"lsl": "980"})
    assert response.status_code == 200
    body = response.json()
    assert body["cpk"] == pytest.approx(0.591, abs=0.001)
    assert body["ppk"] == pytest.approx(0.571, abs=0.001)
    assert body["xbar"]["ucl"] == pytest.approx(1019.54, abs=0.01)
    assert body["n_failures"] == 1
    assert body["verdict"] == "not assessable"
    # every key from analyze() called directly must be identical
    direct = analyze(pd.read_csv(FIXTURE), 980.0, subgroup_col="build_id",
                     order_col="build_date", value_col="uts_mpa")
    for key, value in direct.items():
        assert body[key] == pytest.approx(value)
    assert body["profile"]["name"] == "lpbf"
    assert body["parameters"] == {"columns": [], "usual_range": {}, "flagged_builds": []}


def test_missing_column_is_400_and_names_it():
    response = post_csv("build_id,build_date\nB1,2026-01-01\n", lsl="980")
    assert response.status_code == 400
    assert "uts_mpa" in response.json()["detail"]


def test_unequal_coupons_is_400():
    text = "build_id,build_date,uts_mpa\nB1,2026-01-01,1\nB1,2026-01-01,2\nB2,2026-01-02,3\n"
    response = post_csv(text, lsl="0")
    assert response.status_code == 400
    assert "B2" in response.json()["detail"]


def test_bad_dataset_name_is_404():
    assert client.get("/analyze?dataset=nope&lsl=980").status_code == 404
    assert client.get("/analyze?dataset=..%2Fqc&lsl=980").status_code == 404


def test_flagged_build_reports_parameter_value():
    # 6 steady builds and one build (B7) with a shifted strength and high oxygen
    rows = ["build_id,build_date,uts_mpa,chamber_oxygen_ppm"]
    for i in range(1, 8):
        base, oxygen = (900, 500) if i == 7 else (1000, 100)
        for d in (-10, 0, 10):
            rows.append(f"B{i},2026-01-{i:02d},{base + d},{oxygen}")
    response = post_csv("\n".join(rows) + "\n", lsl="800")
    assert response.status_code == 200
    params = response.json()["parameters"]
    assert params["columns"] == ["chamber_oxygen_ppm"]
    assert params["flagged_builds"] == [
        {"build_id": "B7", "values": {"chamber_oxygen_ppm": 500.0}}]
    assert params["usual_range"]["chamber_oxygen_ppm"] == {"min": 100.0, "max": 100.0}


def test_app_data_matches_data():
    """app/data/ must hold byte-for-byte copies of data/*.csv (run app/sync_data.sh)."""
    def csv_files(folder):
        if not os.path.isdir(folder):
            return {}
        found = {}
        for name in os.listdir(folder):
            if name.endswith(".csv"):
                with open(os.path.join(folder, name), "rb") as f:
                    found[name] = f.read()
        return found
    assert csv_files(os.path.join(ROOT, "app", "data")) == csv_files(os.path.join(ROOT, "data"))
