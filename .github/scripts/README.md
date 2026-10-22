# H-06: deploying AeroQual to Posit Connect

The workflow (`.github/workflows/deploy-fastapi.yml`) and `connect-publish-async.sh` are the
repository's `connect-publish` templates, originally from
[timothyfraser/fastapi-connect-demo](https://github.com/timothyfraser/fastapi-connect-demo) (MIT).
The publisher script is the template copy, unchanged. The workflow adds three things to the
template: it builds the React dashboard, stages a bundle (app source + built dashboard + the six
`data/*.csv` files and codebook) with `prepare-connect-bundle.py`, and runs every test before it
publishes.

## How a deploy happens

Every push to `main` that touches `app/`, `data/` or `.github/` runs **Actions → Deploy FastAPI to
Posit Connect**. You can also start it by hand there (**Run workflow**). The run:

1. tests and builds the dashboard (`npm test`, `npm run build`, Node 22);
2. stages the bundle and checks every file against the committed `app/manifest.json`
   (the manifest is written on a teammate's machine, never in CI);
3. runs `pytest tests`, `demo/check.py` and a local copy of the bundle;
4. publishes. The first run creates the content item `sigma-airlines-aeroqual` on Connect; later
   runs update the same item, so the URL does not change;
5. asks Connect to make the app public ("anyone, no login"). If the server refuses, the run warns:
   set it by hand in Connect (the app's **Access** panel);
6. checks `/health`, then checks the dashboard, the SPEC known answer and all six datasets
   **without** a key, as a judge would see them.

Secrets: `CONNECT_SERVER` and `CONNECT_API_KEY`, set by the repo owner in **Settings → Secrets and
variables → Actions**. Never put either value in a file, commit, log or chat.

## When you change the app, re-write the manifest

The manifest is the packing list: Connect receives only the files it lists, with their checksums.
After changing any Python file, dataset, requirement or the dashboard source, re-write it on your
machine with **Python 3.12** (it must match `app/.python-version`) and Node 22, then commit it with
the change:

```bash
python -m pip install -r app/requirements.txt rsconnect-python==1.32.0
bash app/manifestme.sh      # syncs data, builds the dashboard, writes app/manifest.json
```

If the run fails with "Stale manifest", this step was skipped.

## Deploy from your own machine (optional)

`bash app/deployme.sh` does the same publish from a terminal. It needs `CONNECT_SERVER` and
`CONNECT_API_KEY` in that terminal or in a gitignored `app/.env`, and the dashboard built.

## Local tooling checks

```bash
python .github/scripts/test_connect_bundle.py -v
python .github/scripts/prepare-connect-bundle.py --output "$(mktemp -d)/bundle"
bash -n .github/scripts/connect-publish-async.sh
```

## Local candidate verification and Windows commands

The local usability candidate retains the upstream push-to-deploy workflow and name-based publisher. The removed preflight script, manual-title input, requirements-api.txt and duplicate app/REAME.md are not restored. API integration tests now live in tests/test_bundle_api.py; run `python -m pytest tests`.

A local manifest was generated with rsconnect-python 1.32.0 under Python 3.12.15 for 18 runtime files in the WAAM candidate. The local candidate is prepared for review and has not been pushed or published. Confirm course-server runtime support before publishing. Qualifying pushes to main now attempt deployment automatically; review publisher configuration and release intent before pushing.

From Windows PowerShell at the repository root, after installing Python 3.12:

```powershell
py -3.12 -m venv .venv-connect
.\.venv-connect\Scripts\python.exe -m pip install -r app/requirements.txt rsconnect-python==1.32.0
npm.cmd --prefix app/frontend ci --no-audit --no-fund
npm.cmd --prefix app/frontend run build
.\.venv-connect\Scripts\python.exe .github/scripts/prepare-connect-bundle.py --output .venv-connect/candidate-1 --write-manifest
.\.venv-connect\Scripts\python.exe .github/scripts/verify-connect-app.py --bundle .venv-connect/candidate-1
```

Use a fresh unused output path. Requirements staging explicitly uses UTF-8 and LF on Windows. Never bypass stale-checksum or unexpected-file checks. Manifest generation is local-only and does not publish.

## WAAM release candidate

H-10 adds the WAAM module, explicit profile registry and three additional CSVs to the runtime bundle. The expanded local manifest was regenerated after the source, codebook and frontend changes; all 18 checksums, isolated HTTP behavior and all six LPBF/WAAM scenarios passed. Repeat generation after any further runtime changes. Legacy LPBF API defaults remain supported. No workflow publication is invoked by local tests. A later push to main still triggers deployment; review the expanded manifest before authorizing that push.
