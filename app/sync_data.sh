#!/bin/bash
# sync_data.sh
# Copy the test datasets from ../data/*.csv into app/data/ so they are uploaded with the app.
# Run from anywhere: ./sync_data.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$SCRIPT_DIR/data"

# nullglob: if there are no CSV files yet, the loop simply does nothing.
shopt -s nullglob
for f in "$SCRIPT_DIR"/../data/*.csv; do
  cp "$f" "$SCRIPT_DIR/data/"
  echo "copied $(basename "$f")"
done
echo "Done. Datasets in $SCRIPT_DIR/data"
