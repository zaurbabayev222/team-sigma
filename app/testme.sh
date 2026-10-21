#!/bin/bash

# testme.sh
# A helper script to test the FastAPI app locally.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash "$SCRIPT_DIR/sync_data.sh"
if [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
  npm --prefix "$SCRIPT_DIR/frontend" ci --cache "${AEROQUAL_NPM_CACHE:-/tmp/aeroqual-npm-cache}" --no-audit --no-fund
  npm --prefix "$SCRIPT_DIR/frontend" run build
fi

python -m uvicorn app:app --host 0.0.0.0 --port 8000
