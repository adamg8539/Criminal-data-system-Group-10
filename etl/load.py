import os
import sys
from datetime import datetime, date

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_db_engine():
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "crime_data")

    connection_url = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    return create_engine(connection_url)


# ---------------------------------------------------------------------------
# CRDS-24: Incremental detection
# ---------------------------------------------------------------------------

def get_last_loaded_date(engine) -> date | None:
    """Return the most recent full_date already in dim_date, or None if empty."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(full_date) FROM dim_date"))
        row = result.fetchone()
        return row[0] if row and row[0] is not None else None


def filter_new_records(df: pd.DataFrame, engine) -> tuple[pd.DataFrame, date | None]:
    """
    Keep only rows whose date is strictly after the last loaded date.
    Returns (filtered_df, last_loaded_date).
    """
    last_date = get_last_loaded_date(engine)
    if last_date is None:
        print("[etl.load] No existing data — performing full load.")
        return df, None

    print(f"[etl.load] Last loaded date: {last_date}. Loading only records after this date.")
    new_df = df[pd.to_datetime(df["date"]).dt.date > last_date].copy()
    print(f"[etl.load] Incremental filter: {len(new_df)} new rows (of {len(df)} total).")
    return new_df, last_date


# ---------------------------------------------------------------------------
# Staging
# ---------------------------------------------------------------------------

def load_staging_data(df: pd.DataFrame, engine):
    """Load transformed data into staging table (replace each run)."""
    df.to_sql("staging_crime", engine, if_exists="replace", index=False)
    print(f"[etl.load] {len(df)} rows loaded into staging_crime.")


# ---------------------------------------------------------------------------
# Dimensions + Fact  (CRDS-26: idempotent via ON CONFLICT DO NOTHING)
# ---------------------------------------------------------------------------

def populate_dimensions_and_fact(engine):
    """Populate star schema tables from staging, skipping already-loaded records."""
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO dim_date (
                full_date, year, month, month_name, quarter,
                period_start_date, period_end_date
            )
            SELECT DISTINCT
                date::DATE,
                EXTRACT(YEAR  FROM date::DATE)::INT,
                EXTRACT(MONTH FROM date::DATE)::INT,
                TO_CHAR(date::DATE, 'Mon'),
                'Q' || EXTRACT(QUARTER FROM date::DATE)::INT,
                DATE_TRUNC('month', date::DATE)::DATE,
                (DATE_TRUNC('month', date::DATE) + INTERVAL '1 month - 1 day')::DATE
            FROM staging_crime
            ON CONFLICT (full_date) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO dim_location (lga, region, state)
            SELECT DISTINCT
                lga,
                COALESCE(region, 'Other'),
                'NSW'
            FROM staging_crime
            ON CONFLICT (lga) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO dim_offence (offence_category, offence_subcategory, offence_group)
            SELECT DISTINCT
                offence_category,
                offence_subcategory,
                COALESCE(offence_group, 'Other')
            FROM staging_crime
            ON CONFLICT (offence_category, offence_subcategory) DO NOTHING;
        """))

        # CRDS-26: ON CONFLICT DO NOTHING prevents duplicate fact rows
        conn.execute(text("""
            INSERT INTO fact_crime (date_id, location_id, offence_id, incident_count)
            SELECT
                d.date_id,
                l.location_id,
                o.offence_id,
                s.incident_count
            FROM staging_crime s
            JOIN dim_date     d ON s.date::DATE = d.full_date
            JOIN dim_location l ON s.lga = l.lga
            JOIN dim_offence  o
              ON s.offence_category    = o.offence_category
             AND s.offence_subcategory = o.offence_subcategory
            ON CONFLICT (date_id, location_id, offence_id) DO NOTHING;
        """))

    print("[etl.load] Dimensions and fact table populated.")


# ---------------------------------------------------------------------------
# CRDS-23: ETL Load History
# ---------------------------------------------------------------------------

def log_load_history(
    engine,
    *,
    rows_extracted: int,
    rows_after_validation: int,
    rows_transformed: int,
    rows_loaded: int,
    incremental_from: date | None,
    status: str,
    error_message: str | None = None,
):
    """Insert a record into etl_load_history for auditability (NFR-14)."""
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO etl_load_history (
                    run_at, rows_extracted, rows_after_validation,
                    rows_transformed, rows_loaded,
                    incremental_from, status, error_message
                ) VALUES (
                    :run_at, :rows_extracted, :rows_after_validation,
                    :rows_transformed, :rows_loaded,
                    :incremental_from, :status, :error_message
                )
            """),
            {
                "run_at": datetime.utcnow(),
                "rows_extracted": rows_extracted,
                "rows_after_validation": rows_after_validation,
                "rows_transformed": rows_transformed,
                "rows_loaded": rows_loaded,
                "incremental_from": incremental_from,
                "status": status,
                "error_message": error_message,
            },
        )
    print(f"[etl.load] Load history recorded: status={status}, rows_loaded={rows_loaded}.")


if __name__ == "__main__":
    engine = get_db_engine()
    processed_file = Path("data/processed/crime_long_format.csv")
    df = pd.read_csv(processed_file, parse_dates=["date"])

    incremental_df, last_date = filter_new_records(df, engine)
    load_staging_data(incremental_df, engine)
    populate_dimensions_and_fact(engine)
    log_load_history(
        engine,
        rows_extracted=len(df),
        rows_after_validation=len(df),
        rows_transformed=len(df),
        rows_loaded=len(incremental_df),
        incremental_from=last_date,
        status="success",
    )
