#!/usr/bin/env bash
# Package app/ + the harbourline library and deploy the Databricks App (run as your own user profile).
set -euo pipefail
APP=${APP:-harbourline-dealroom}
rm -rf build/app && mkdir -p build/app && cp -R app/. build/app/ && cp -R src/harbourline build/app/harbourline && cp -R ai/prompts build/app/prompts
find build/app -name __pycache__ -type d -prune -exec rm -r {} +
databricks workspace import-dir build/app "/Workspace/Users/jennifer.wang@databricks.com/apps/$APP" --overwrite --profile hunter >/dev/null
databricks apps deploy "$APP" --source-code-path "/Workspace/Users/jennifer.wang@databricks.com/apps/$APP" --profile hunter
