#!/usr/bin/env bash
# Publish only the reviewed, checksummed bundle to the confirmed existing target.
# Requires Bash 4+ for the shared publisher; GitHub Actions provides it.
set -euo pipefail
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
  echo 'Use Bash 4+ or the manual GitHub Actions workflow for publishing.' >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
cd "$REPO_DIR"
python .github/scripts/preflight-connect.py
python .github/scripts/prepare-connect-bundle.py --output "$WORK_DIR/bundle"
export BUNDLE_DIR="$WORK_DIR/bundle"
export CONTENT_NAME="sigma-airlines-aeroqual"
bash .github/scripts/connect-publish-async.sh
