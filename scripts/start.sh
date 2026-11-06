#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/python || ! -d frontend/dist ]]; then
  echo 'Run bash scripts/setup.sh first.' >&2
  exit 1
fi
exec .venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
