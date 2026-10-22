"""AeroQual API: X-bar and S chart, Cpk, Ppk and a verdict for tensile-test builds.

This file only reads input and calls analyze() in qc.py. No statistics are computed here
(the only arithmetic is min / max / mean of process parameters, shown for information).
"""
import io
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Import trap: on Posit Connect only this folder is uploaded and app.py is the top-level
# module, so "from app.qc import ..." would fail there. When we run from inside app/, the
# name "app" is this very file. So we put this folder on sys.path and import the other
# files as top-level modules. This works from the repo root and from inside app/.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from qc import analyze  # noqa: E402
from profiles.lpbf import PROFILE  # noqa: E402

# Datasets live in the data folder next to this file (copied by sync_data.sh).
DATA_DIR = os.path.join(APP_DIR, "data")

app = FastAPI(
    title="AeroQual API",
    description="Process control and capability of tensile strength by build (LPBF titanium).",
    version="1.0.0",
)

# Let a browser frontend on another address call this API. Fine for a hackathon demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def parameter_summary(df, result):
    """Describe the optional process parameters (min / max / mean only, no statistics).

    The usual range is over build-level means of builds that are NOT flagged.
    """
    columns = [p["column"] for p in PROFILE["parameters"] if p["column"] in df.columns]
    if not columns:
        return {"columns": [], "usual_range": {}, "flagged_builds": []}

    table = pd.DataFrame({"build_id": df[PROFILE["subgroup_col"]].astype(str)})
    for col in columns:
        table[col] = pd.to_numeric(df[col], errors="coerce")
    per_build = table.groupby("build_id", sort=False).mean()  # one mean per build

    flagged_ids = [b["build_id"] for b in result["builds"] if b["flagged"]]
    normal = per_build.drop(index=flagged_ids, errors="ignore")

    usual_range = {}
    for col in columns:
        values = normal[col].dropna()
        if len(values) > 0:
            usual_range[col] = {"min": float(values.min()), "max": float(values.max())}

    flagged = []
    for build_id in flagged_ids:
        row = per_build.loc[build_id]
        values = {col: (None if pd.isna(row[col]) else float(row[col])) for col in columns}
        flagged.append({"build_id": build_id, "values": values})
    return {"columns": columns, "usual_range": usual_range, "flagged_builds": flagged}


def run_analysis(df, lsl, min_builds, cpk_target):
    """Check the columns, call analyze(), and add the profile and parameter info."""
    for col in (PROFILE["subgroup_col"], PROFILE["order_col"], PROFILE["value_col"]):
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"missing column '{col}'")
    try:
        result = analyze(
            df, lsl,
            subgroup_col=PROFILE["subgroup_col"],
            order_col=PROFILE["order_col"],
            value_col=PROFILE["value_col"],
            min_builds=min_builds,
            cpk_target=cpk_target,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    result["profile"] = {k: PROFILE[k] for k in ("name", "label", "value_label", "value_unit")}
    result["parameters"] = parameter_summary(df, result)
    # Add plot-ready bins without changing any existing H-04 response fields.
    counts, edges = np.histogram(pd.to_numeric(df[PROFILE["value_col"]]), bins="auto")
    result["histogram"] = [{"lower": float(edges[i]), "upper": float(edges[i + 1]),
                            "count": int(count)} for i, count in enumerate(counts)]
    return result


@app.get("/")
async def root(request: Request):
    """Send visitors to the dashboard. On Posit Connect the app lives under a path
    prefix (root_path), so the redirect must include it."""
    prefix = request.scope.get("root_path", "").rstrip("/")
    return RedirectResponse(url=prefix + "/dashboard/")


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/datasets")
async def datasets():
    """List the built-in datasets (CSV file names without .csv)."""
    if not os.path.isdir(DATA_DIR):
        return {"datasets": []}
    names = [f[:-4] for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return {"datasets": sorted(names)}


@app.get("/analyze")
def analyze_dataset(dataset: str, lsl: float, min_builds: int = 25, cpk_target: float = 1.33):
    """Analyze a built-in dataset, e.g. /analyze?dataset=stable_capable&lsl=900."""
    # Only letters, digits, _ and - are allowed: no slashes, no "..".
    if not re.fullmatch(r"[A-Za-z0-9_-]+", dataset):
        raise HTTPException(status_code=404, detail=f"unknown dataset '{dataset}'")
    path = os.path.join(DATA_DIR, dataset + ".csv")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"unknown dataset '{dataset}'")
    return run_analysis(pd.read_csv(path), lsl, min_builds, cpk_target)


@app.post("/analyze")
def analyze_upload(file: UploadFile = File(...), lsl: float = Form(...),
                   min_builds: int = Form(25), cpk_target: float = Form(1.33)):
    """Analyze an uploaded CSV (multipart form: file, lsl, min_builds, cpk_target)."""
    try:
        df = pd.read_csv(io.BytesIO(file.file.read()))
    except Exception:
        raise HTTPException(status_code=400, detail="could not read the file as a CSV table")
    return run_analysis(df, lsl, min_builds, cpk_target)


@app.get("/__docs__/")
async def docs_redirect():
    """Redirect to FastAPI interactive documentation."""
    return RedirectResponse(url="/docs")


# Keep GET / as the existing API health message; serve H-05 separately.
FRONTEND_DIR = Path(APP_DIR) / "frontend" / "dist"
if FRONTEND_DIR.is_dir():
    app.mount("/dashboard", StaticFiles(directory=FRONTEND_DIR, html=True), name="dashboard")
