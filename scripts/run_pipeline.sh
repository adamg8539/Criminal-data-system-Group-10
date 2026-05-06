#!/usr/bin/env bash
# Runs the full ETL pipeline from the project root.
# Usage: bash scripts/run_pipeline.sh [--full]
#   --full  Skip incremental detection and reload everything.
# Reads DB credentials from .env in the project root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
VENV="$PROJECT_ROOT/venv"

FULL_LOAD=false
for arg in "$@"; do
  [[ "$arg" == "--full" ]] && FULL_LOAD=true
done

# Load .env
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env file not found at $ENV_FILE"
  echo "Copy .env.example to .env and fill in your credentials."
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

# Activate virtualenv
if [[ -f "$VENV/bin/activate" ]]; then
  source "$VENV/bin/activate"
else
  echo "WARNING: virtualenv not found at $VENV — using system Python."
fi

cd "$PROJECT_ROOT"

if [[ "$FULL_LOAD" == "true" ]]; then
  echo "==> Full load requested — clearing fact_crime and dim_date for reload..."
  export PGPASSWORD="${DB_PASSWORD:-password}"
  psql -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" \
       -U "${DB_USER:-postgres}" -d "${DB_NAME:-crime_data}" <<'SQL'
TRUNCATE fact_crime, dim_date, dim_location, dim_offence RESTART IDENTITY CASCADE;
SQL
fi

echo "==> Starting ETL pipeline at $(date)..."
python3 -m etl.pipeline
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
  echo "==> Pipeline finished successfully at $(date)."
else
  echo "==> Pipeline FAILED (exit code $EXIT_CODE) at $(date)." >&2
  exit $EXIT_CODE
fi
