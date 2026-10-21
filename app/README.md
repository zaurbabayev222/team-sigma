# AeroQual API and dashboard

This integration preserves the completed H-04 API and its `app:app` deployment entrypoint.
The statistics remain in the unchanged `qc.py`. The React dashboard renders Python results.

From the repository root, activate a Python 3.12 environment with the pinned dependencies:

```bash
source /tmp/aeroqual-venv/bin/activate  # or activate your own environment
python -m pip install -r app/requirements.txt
bash app/testme.sh
```

The startup script syncs `data/*.csv` into `app/data/`, installs/builds the frontend and starts
Uvicorn on port 8000. Python 3.12, Node/npm and internet access for uncached dependencies are needed.
Stop with Ctrl-C. Open the dashboard at `http://127.0.0.1:8000/dashboard/`.

| Route | Behavior |
| --- | --- |
| `GET /` | Existing API status JSON |
| `GET /health` | Existing JSON status `ok` |
| `GET /datasets` | Dataset identifiers **without `.csv`**, e.g. `stable_capable` |
| `GET /analyze` | `dataset`, `lsl`; optional `min_builds=25`, `cpk_target=1.33` |
| `POST /analyze` | Multipart `file` CSV and `lsl`; same optional settings |
| `GET /docs` | Interactive API documentation |
| `GET /dashboard/` | Built React dashboard and assets |

Required CSV columns: `build_id`, `build_date`, `uts_mpa` (MPa). Optional process columns and
units are documented in `../data/README.md`. The response preserves the existing core, profile
and `parameters` object (`columns`, `usual_range`, `flagged_builds`), with an additive `histogram`
list of `{lower, upper, count}` bins. The frontend adapts that existing parameter contract and
uses API routes one directory above `/dashboard/`, including under a Connect content prefix.

```bash
curl --fail 'http://127.0.0.1:8000/analyze?dataset=stable_capable&lsl=895'
python demo/check.py --base-url http://127.0.0.1:8000
python -m pytest tests app/test_api.py
```

See `../demo/README.md` for the three examples and captured outputs. See
`../.github/scripts/README.md` for the deployment handoff. `manifestme.sh` regenerates the manifest
locally using the shared preparation tool (install rsconnect-python 1.32.0 first).
`deployme.sh` preflights a human-confirmed existing target and publishes the verified bundle;
startup and tests never invoke publishing. Credentials belong in the environment or repository
secrets. No publication has been performed by this integration.
