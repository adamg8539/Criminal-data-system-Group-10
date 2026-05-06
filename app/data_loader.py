import pandas as pd
from pathlib import Path

_cache: pd.DataFrame | None = None

def load_data() -> pd.DataFrame:
    global _cache
    if _cache is not None:
        return _cache

    csv_path = Path(__file__).parent.parent / "data/processed/crime_long_format.csv"
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")

    # Add region if missing
    if "region" not in df.columns:
        from etl.transform import LGA_REGION_MAP
        df["region"] = df["lga"].map(LGA_REGION_MAP).fillna("Other")

    # Add offence_group if missing
    if "offence_group" not in df.columns:
        from etl.transform import OFFENCE_GROUP_MAP
        df["offence_group"] = df["offence_category"].map(OFFENCE_GROUP_MAP).fillna("Other")

    _cache = df
    return df
