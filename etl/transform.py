import pandas as pd

ID_COLUMNS = ["LGA", "Offence category", "Subcategory"]


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the dataset from wide format to long format."""
    df = df.dropna(subset=ID_COLUMNS)

    date_columns = [col for col in df.columns if col not in ID_COLUMNS]

    df_long = df.melt(
        id_vars=ID_COLUMNS,
        value_vars=date_columns,
        var_name="date",
        value_name="incident_count",
    )

    df_long["date"] = pd.to_datetime(df_long["date"], errors="coerce")
    df_long = df_long.dropna(subset=["date", "incident_count"])

    df_long = df_long.rename(
        columns={
            "LGA": "lga",
            "Offence category": "offence_category",
            "Subcategory": "offence_subcategory",
        }
    )

    df_long["incident_count"] = df_long["incident_count"].astype(int)

    return df_long


if __name__ == "__main__":
    from etl.extract import extract_data
    from pathlib import Path

    raw_df = extract_data()
    transformed_df = transform_data(raw_df)

    output_file = Path("data/processed/crime_long_format.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    transformed_df.to_csv(output_file, index=False)

    print(f"Saved transformed data to {output_file}")
    print(transformed_df.head())
    print(transformed_df.shape)