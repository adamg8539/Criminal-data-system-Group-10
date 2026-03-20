import os
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


def load_staging_data(df: pd.DataFrame):
    """Load transformed data into staging table."""
    engine = get_db_engine()
    df.to_sql("staging_crime", engine, if_exists="replace", index=False)
    print("Data loaded into staging_crime table.")


def populate_dimensions_and_fact():
    """Populate star schema tables from staging table."""
    engine = get_db_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO dim_date (full_date, year, month, month_name, quarter)
            SELECT DISTINCT
                date,
                EXTRACT(YEAR FROM date)::INT,
                EXTRACT(MONTH FROM date)::INT,
                TO_CHAR(date, 'Month'),
                EXTRACT(QUARTER FROM date)::INT
            FROM staging_crime
            ON CONFLICT (full_date) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO dim_location (lga, state)
            SELECT DISTINCT
                lga,
                'NSW'
            FROM staging_crime
            ON CONFLICT (lga) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO dim_offence (offence_category, offence_subcategory)
            SELECT DISTINCT
                offence_category,
                offence_subcategory
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
            JOIN dim_date d ON s.date = d.full_date
            JOIN dim_location l ON s.lga = l.lga
            JOIN dim_offence o
              ON s.offence_category = o.offence_category
             AND s.offence_subcategory = o.offence_subcategory;
        """))

    print("Dimensions and fact table populated successfully.")


if __name__ == "__main__":
    processed_file = Path("data/processed/crime_long_format.csv")
    df = pd.read_csv(processed_file, parse_dates=["date"])

    load_staging_data(df)
    populate_dimensions_and_fact()