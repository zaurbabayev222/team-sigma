# H-06: deploying AeroQual to Posit Connect

The workflow (`.github/workflows/deploy-fastapi.yml`) and `connect-publish-async.sh` are the
repository's `connect-publish` templates, originally from
[timothyfraser/fastapi-connect-demo](https://github.com/timothyfraser/fastapi-connect-demo) (MIT).
The publisher script is the template copy, unchanged. The workflow adds three things to the
template: it builds the React dashboard, stages a bundle (app source + built dashboard + the three
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
6. checks `/health`, then checks the dashboard, the SPEC known answer and all three datasets
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
