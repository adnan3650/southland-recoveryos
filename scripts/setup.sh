#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/python ]]; then
  python3.12 -m venv .venv
fi
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -r backend/requirements.lock.txt
npm --prefix frontend ci
npm --prefix frontend run build
printf '\nReady. Run: bash scripts/start.sh\nOpen: http://127.0.0.1:8000\n'
