#!/usr/bin/env bash
# Generate the synthetic raw data locally and upload it to the Unity Catalog volumes (the Lakeflow landing zone).
set -euo pipefail
P=${PROFILE:-hunter}
CAT=$(uv run python -c "import yaml;d=yaml.safe_load(open('config/demo.yml'));print(d['catalog'])")
OUT=${OUT:-/tmp/hl_build/dealroom}
rm -rf "$OUT" && uv run --extra dev python data/gen_dealroom.py "$OUT"
V="dbfs:/Volumes/$CAT/vdr"
databricks fs cp -r "$OUT/deal_rooms" "$V/deal_rooms/" --overwrite --profile "$P"
databricks fs cp -r "$OUT/staged_uploads" "$V/portal_uploads/_staged/" --overwrite --profile "$P"
databricks fs mkdir "$V/deal_rooms/_staging_tables" --profile "$P"
for f in "$OUT"/*.csv data/seed/external_factors_seed.csv; do databricks fs cp "$f" "$V/deal_rooms/_staging_tables/" --overwrite --profile "$P"; done
echo "uploaded raw data to $V"
