#!/usr/bin/env bash
# deployme.sh
#
# Deploy AeroQual to Posit Connect from your own machine (the GitHub Actions
# workflow does the same on every push to main; prefer that).
# Needs CONNECT_SERVER and CONNECT_API_KEY in your terminal or in a gitignored
# app/.env, the dashboard built (npm --prefix app/frontend run build), and a
# committed app/manifest.json that matches (bash app/manifestme.sh).
set -euo pipefail
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
  echo 'Use Bash 4+ or the GitHub Actions workflow for publishing.' >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Optional: load CONNECT_SERVER and CONNECT_API_KEY from app/.env
if [ -f "$SCRIPT_DIR/.env" ]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env"
fi
: "${CONNECT_SERVER:?Set CONNECT_SERVER (terminal or app/.env)}"
: "${CONNECT_API_KEY:?Set CONNECT_API_KEY (terminal or app/.env)}"
export CONNECT_SERVER CONNECT_API_KEY

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
cd "$REPO_DIR"
python .github/scripts/prepare-connect-bundle.py --output "$WORK_DIR/bundle"
export BUNDLE_DIR="$WORK_DIR/bundle"
export CONTENT_NAME="sigma-airlines-aeroqual"
export CONTENT_TITLE="AeroQual (Sigma Airlines)"
bash .github/scripts/connect-publish-async.sh
