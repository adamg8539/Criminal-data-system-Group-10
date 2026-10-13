#!/usr/bin/env bash
# Applies the star schema to the PostgreSQL database configured in .env.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  .venv/Scripts/python.exe scripts/setup_db.py
elif [[ -x ".venv/bin/python" ]]; then
  .venv/bin/python scripts/setup_db.py
else
  python scripts/setup_db.py
fi
