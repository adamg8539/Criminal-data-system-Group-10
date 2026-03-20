from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_fact_table


def run_pipeline():
    print("Starting ETL pipeline...")

    raw_df = extract_data()
    print(f"Extracted {raw_df.shape[0]} rows and {raw_df.shape[1]} columns.")

    transformed_df = transform_data(raw_df)
    print(
        f"Transformed into {transformed_df.shape[0]} rows and {transformed_df.shape[1]} columns."
    )

    load_fact_table(transformed_df)

    print("ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()