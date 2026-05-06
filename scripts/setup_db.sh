#!/usr/bin/env bash
# Sets up the PostgreSQL database and applies the star schema.
# Usage: bash scripts/setup_db.sh
# Reads DB credentials from .env in the project root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
SCHEMA_FILE="$PROJECT_ROOT/database/schema.sql"

# Load .env
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env file not found at $ENV_FILE"
  echo "Copy .env.example to .env and fill in your credentials."
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-password}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-crime_data}"

export PGPASSWORD="$DB_PASSWORD"

echo "==> Checking PostgreSQL connection..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c '\q' postgres \
  || { echo "ERROR: Cannot connect to PostgreSQL. Check your .env credentials."; exit 1; }

echo "==> Creating database '$DB_NAME' (skipping if it already exists)..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" postgres \
  -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" \
  | grep -q 1 \
  || psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" postgres \
     -c "CREATE DATABASE $DB_NAME;"

echo "==> Dropping existing tables (clean slate)..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'SQL'
DROP TABLE IF EXISTS fact_crime        CASCADE;
DROP TABLE IF EXISTS dim_date          CASCADE;
DROP TABLE IF EXISTS dim_location      CASCADE;
DROP TABLE IF EXISTS dim_offence       CASCADE;
DROP TABLE IF EXISTS staging_crime     CASCADE;
DROP TABLE IF EXISTS etl_load_history  CASCADE;
SQL

echo "==> Applying schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"

echo "==> Schema applied successfully."
echo "    Tables created: dim_date, dim_location, dim_offence, fact_crime, etl_load_history"
