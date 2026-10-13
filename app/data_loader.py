import pandas as pd
from sqlalchemy import text

from etl.load import get_db_engine

_cache: pd.DataFrame | None = None

DATA_QUERY = text("""
    SELECT
        d.full_date AS date,
        d.year,
        d.month,
        d.month_name,
        l.lga,
        l.region,
        o.offence_category,
        o.offence_subcategory,
        o.offence_group,
        f.incident_count
    FROM fact_crime AS f
    JOIN dim_date AS d ON f.date_id = d.date_id
    JOIN dim_location AS l ON f.location_id = l.location_id
    JOIN dim_offence AS o ON f.offence_id = o.offence_id
""")


def load_data() -> pd.DataFrame:
    global _cache
    if _cache is not None:
        return _cache

    engine = get_db_engine()
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(
                DATA_QUERY,
                connection,
                parse_dates=["date"],
            )
    finally:
        engine.dispose()

    _cache = df
    return df
