#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m ruff check backend tests
.venv/bin/python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
# Start the app in another terminal, then: npm --prefix frontend run test:e2e
