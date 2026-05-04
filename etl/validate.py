import sys
import pandas as pd

REQUIRED_COLUMNS = [
    "lga", "offence_category", "offence_subcategory",
    "date", "incident_count",
]
MIN_YEAR = 1995
MAX_YEAR = 2030


def validate_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Run validation rules against the transformed DataFrame.

    Returns (cleaned_df, report) where report contains counts of
    rows dropped by each rule.
    """
    report = {
        "input_rows": len(df),
        "missing_required_fields": 0,
        "negative_incident_count": 0,
        "invalid_date_range": 0,
        "rows_passed": 0,
    }

    # Rule 1: no nulls in required columns
    null_mask = df[REQUIRED_COLUMNS].isnull().any(axis=1)
    n_null = null_mask.sum()
    if n_null:
        print(f"[etl.validate] Dropped {n_null} rows with missing required fields.", file=sys.stderr)
    report["missing_required_fields"] = int(n_null)
    df = df[~null_mask].copy()

    # Rule 2: incident_count must be >= 0
    neg_mask = df["incident_count"] < 0
    n_neg = neg_mask.sum()
    if n_neg:
        print(f"[etl.validate] Dropped {n_neg} rows with negative incident_count.", file=sys.stderr)
    report["negative_incident_count"] = int(n_neg)
    df = df[~neg_mask].copy()

    # Rule 3: year must be within expected range
    years = pd.to_datetime(df["date"]).dt.year
    range_mask = ~years.between(MIN_YEAR, MAX_YEAR)
    n_range = range_mask.sum()
    if n_range:
        print(f"[etl.validate] Dropped {n_range} rows with year outside {MIN_YEAR}–{MAX_YEAR}.", file=sys.stderr)
    report["invalid_date_range"] = int(n_range)
    df = df[~range_mask].copy()

    report["rows_passed"] = len(df)
    total_dropped = report["input_rows"] - report["rows_passed"]
    print(f"[etl.validate] Validation complete: {report['rows_passed']} rows passed, {total_dropped} dropped.")
    return df, report


if __name__ == "__main__":
    from etl.extract import extract_data
    from etl.transform import transform_data

    raw_df = extract_data()
    transformed_df = transform_data(raw_df)
    clean_df, report = validate_data(transformed_df)
    print("Validation report:", report)
