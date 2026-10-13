import os
from datetime import datetime, date
from tempfile import SpooledTemporaryFile

import pandas as pd
from sqlalchemy import URL, create_engine, text
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_db_engine():
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "crime_data")
    db_sslmode = os.getenv("DB_SSLMODE", "require")

    connection_url = URL.create(
        "postgresql+psycopg2",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
    )
    return create_engine(connection_url, connect_args={"sslmode": db_sslmode})


# ---------------------------------------------------------------------------
# Atomic staging + upsert
# ---------------------------------------------------------------------------

STAGING_COLUMNS = [
    "date",
    "lga",
    "region",
    "offence_category",
    "offence_subcategory",
    "offence_group",
    "incident_count",
]


def _copy_to_staging(conn, df: pd.DataFrame):
    """Bulk-copy the transformed rows through the active transaction."""
    with SpooledTemporaryFile(
        max_size=8 * 1024 * 1024,
        mode="w+",
        encoding="utf-8",
        newline="",
    ) as csv_stream:
        df[STAGING_COLUMNS].to_csv(
            csv_stream,
            index=False,
            header=False,
            na_rep=r"\N",
            date_format="%Y-%m-%d",
        )
        csv_stream.seek(0)

        cursor = conn.connection.driver_connection.cursor()
        try:
            cursor.copy_expert(
                """
                COPY staging_crime (
                    date, lga, region, offence_category,
                    offence_subcategory, offence_group, incident_count
                )
                FROM STDIN WITH (FORMAT CSV, NULL '\\N')
                """,
                csv_stream,
            )
        finally:
            cursor.close()


def load_data_atomic(df: pd.DataFrame, engine) -> int:
    """Stage and upsert one complete BOCSAR snapshot in one transaction."""
    if df.empty:
        return 0

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TEMP TABLE staging_crime (
                date DATE NOT NULL,
                lga VARCHAR(100) NOT NULL,
                region VARCHAR(100) NOT NULL,
                offence_category VARCHAR(100) NOT NULL,
                offence_subcategory VARCHAR(150) NOT NULL,
                offence_group VARCHAR(50) NOT NULL,
                incident_count INT NOT NULL CHECK (incident_count >= 0),
                UNIQUE (date, lga, offence_category, offence_subcategory)
            ) ON COMMIT DROP;
        """))

        _copy_to_staging(conn, df)

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
            ON CONFLICT (date_id, location_id, offence_id)
            DO UPDATE SET incident_count = EXCLUDED.incident_count;
        """))

    print(f"[etl.load] Atomically upserted {len(df)} rows.")
    return len(df)


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

    rows_loaded = load_data_atomic(df, engine)
    log_load_history(
        engine,
        rows_extracted=len(df),
        rows_after_validation=len(df),
        rows_transformed=len(df),
        rows_loaded=rows_loaded,
        incremental_from=None,
        status="success",
    )
