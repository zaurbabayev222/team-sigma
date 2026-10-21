# H-06: Posit Connect handoff

The workflow and publisher adapt the repository's `connect-publish` templates, originally from [timothyfraser/fastapi-connect-demo](https://github.com/timothyfraser/fastapi-connect-demo) (MIT). Changes preserve the completed H-04 `app:app` layout, include the built frontend and three synthetic CSVs, check file checksums, and require a manually confirmed existing Connect target. Pushes and pull requests validate; only a manual workflow run publishes.

## Current status

The API, dashboard and three synthetic datasets are present. **A genuine `app/manifest.json` has been generated locally with rsconnect-python 1.32.0**, recording Python 3.12.4 and 14 runtime files. Both local generation and the CI-style reconstruction verified every file checksum. The isolated bundle passed the HTML/dashboard-asset check, JSON health check, SPEC known-answer upload and all three scenario/API parity checks. The five bundle contract tests also pass.

No deployment, commit or push has been performed. GitHub CLI is not authenticated on this machine, and course Connect publisher access has not been provided. A teammate with the appropriate access must perform the remaining remote steps. Repository ownership and Connect publisher access are separate permissions. Confirm that the course server supports the Python version recorded in the manifest before publishing.

## Remaining steps for the publishing teammate

1. Obtain the **course Posit Connect** publisher access/key. The GitHub token is not the Connect API key. Review the application and deployment changes locally.
2. Identify the team's existing AeroQual content item on Connect, or have an authorized publisher/course administrator provision it once. Confirm its exact title and GUID and configure public access for the judges. Do not use another team's content GUID.
3. In the GitHub repository, open **Settings → Secrets and variables → Actions**. Set repository secrets **CONNECT_SERVER** and **CONNECT_API_KEY**, and repository variable **CONNECT_CONTENT_GUID**. Only names, not secret values, belong in this handoff.
4. Review and authorize the Git changes. Commit/push the complete application, frontend source/lockfile, datasets, demo checks, `.github/` workflow/scripts and `app/manifest.json` together. The manifest must match the same source/data/UI revision. These actions have not been performed by the agent.
5. On the default branch, open **Actions → Validate and deploy AeroQual → Run workflow**. Enter the exact confirmed Connect content title. Pushes run validation only; the manual run is what publishes.
6. Require the entire run to pass, including unauthenticated `/dashboard/` assets and `/health`, known-answer upload and all three example analyses. Then open the published dashboard in a private/logged-out browser and reproduce the documented results. Record the run and successful public verification in H-06 only after this succeeds.

If a checksum check fails, rebuild and regenerate the manifest **locally** using the instructions below. Do not bypass the check or regenerate a Python manifest on the CI runner. If the course server lacks the required Python interpreter, select an available compatible version, regenerate and test locally, and review the resulting manifest before retrying.

## Regenerate and verify locally when the app changes

Use Python 3.12 in a virtual environment. The current local environment is `/tmp/aeroqual-venv`; activate it or use its Python explicitly. Install the application and publishing tool with:

```bash
source /tmp/aeroqual-venv/bin/activate
python -m pip install -r app/requirements-api.txt rsconnect-python==1.32.0
```

The application requirements include pinned FastAPI, Uvicorn and python-multipart. The publishing tool is local-only and is not installed in the deploy job. Build with the same lockfile and Node version as CI (22):

```bash
npm --prefix app/frontend ci
npm --prefix app/frontend test
npm --prefix app/frontend run build
python -m pytest tests
python demo/check.py
```

Start the application with `bash app/testme.sh` and verify its local API using `python demo/check.py --base-url http://127.0.0.1:8000`. Then generate the manifest **locally**, from a fresh temporary bundle directory:

```bash
python .github/scripts/prepare-connect-bundle.py --output /tmp/aeroqual-release-1 --write-manifest
```

Choose a new unused temporary path each time. The script stages only Python app source, the built `app/frontend/dist/`, the three specified `data/*.csv` files and codebook, requirements, and `.python-version`. The bundle preserves H-04's flat `app.py`, `qc.py`, `profiles/` and `data/` layout; the explicit entrypoint is `app:app`. The existing JSON API root remains unchanged and the frontend is served at `/dashboard/`. The H-04 API must report JSON `{"status":"ok"}` at `/health`, discover the bundled `data/` directory, and accept multipart `file` + `lsl` at `/analyze`.

The manifest is copied to `app/manifest.json` only after verification. Review the manifest file list before publishing. A source, data, requirements or Python change, or a frontend rebuild that changes output bytes, requires regenerating this manifest. CI rejects missing, extra or modified files instead of silently uploading stale code. The manifest is committed; generated temporary bundles, environments, credentials, `node_modules` and `dist` are not.

Verify the prepared application independently of the source checkout:

```bash
python .github/scripts/verify-connect-app.py --bundle /tmp/aeroqual-release-1
```

This launches the bundle temporarily, verifies the HTML dashboard and its JavaScript/CSS assets and unauthenticated JSON health endpoint, uploads the SPEC arithmetic example, and checks the X-bar/S limits, Cpk/Ppk, counts and verdict. It also runs the three-dataset checker against that isolated bundle's API. It stops only the process it started. It does not substitute for teammate browser reproduction or a real Connect deployment.

To emulate CI without regenerating the manifest, use another fresh path:

```bash
python .github/scripts/prepare-connect-bundle.py --output /tmp/aeroqual-ci-check-1
python .github/scripts/verify-connect-app.py --bundle /tmp/aeroqual-ci-check-1
```

## Configure the target without committing credentials

An authorized human must provision the course Posit Connect content item once, select public access for the judges, and confirm its title. Set repository Actions secrets `CONNECT_SERVER` and `CONNECT_API_KEY`, and repository variable `CONNECT_CONTENT_GUID` to that existing item's GUID. Keep both secret values out of source, documentation, chat and logs. This tooling neither creates content by name nor changes content permissions.

The deployment lifecycle skill requires human code review and confirmation of the exact target before publishing. With the secrets and target exported in the human's terminal, a read-only check is:

```bash
python .github/scripts/preflight-connect.py
```

It reads `CONNECT_SERVER`, `CONNECT_API_KEY`, `CONTENT_GUID`, and `CONFIRMED_CONTENT_TITLE` from the environment, prints the title and GUID, checks public access and refuses a mismatched title. Never paste a key into chat or a command argument.

## Publish only when authorized

No commit or push has been performed for this work. After the human reviews and authorizes the exact change, commit the manifest alongside its source changes. Once the workflow exists on the default branch, an authorized human can use GitHub Actions → **Validate and deploy AeroQual** → **Run workflow**, supplying the exact confirmed title. Do not trigger publication merely to test configuration.

The workflow tests the frontend, Python statistics, all three scenarios, manifest checksums and the actual staged HTTP app before any server mutation. Publishing streams the Connect task output; a detached task is not reported as a completed deployment. Subsequent checks must pass without an Authorization header: HTML dashboard, JSON `/health`, known-answer CSV upload and all three dataset analyses. No public URL or green workflow has been verified yet.

H-06 is complete only after a green actual run, an independently opened logged-out dashboard, and matching analysis results. Record those outcomes in the task ledger; do not mark it done on the strength of local tests alone.

## Local tooling checks

```bash
python .github/scripts/test_connect_bundle.py -v
bash -n .github/scripts/connect-publish-async.sh
```

These use disposable unit-test fixtures, not demonstration datasets or a real server.
