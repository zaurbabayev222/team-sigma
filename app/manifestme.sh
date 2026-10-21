#!/usr/bin/env bash
# Generate locally using the same flat app:app bundle that CI verifies.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
bash "$SCRIPT_DIR/sync_data.sh"
npm --prefix "$SCRIPT_DIR/frontend" run build
cd "$REPO_DIR"
python .github/scripts/prepare-connect-bundle.py --output "$WORK_DIR/bundle" --write-manifest
