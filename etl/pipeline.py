import sys
from etl.extract import extract_data
from etl.transform import transform_data
from etl.validate import validate_data
from etl.load import (
    get_db_engine,
    filter_new_records,
    load_staging_data,
    populate_dimensions_and_fact,
    log_load_history,
)


def run_pipeline():
    print("[pipeline] Starting ETL pipeline...")
    engine = get_db_engine()

    rows_extracted = rows_validated = rows_transformed = rows_loaded = 0
    incremental_from = None

    try:
        # Extract
        raw_df = extract_data()
        rows_extracted = len(raw_df)
        print(f"[pipeline] Extracted {raw_df.shape[0]} rows, {raw_df.shape[1]} columns.")

        # Transform
        transformed_df = transform_data(raw_df)
        rows_transformed = len(transformed_df)
        print(f"[pipeline] Transformed to {rows_transformed} rows.")

        # Validate (CRDS-27)
        validated_df, validation_report = validate_data(transformed_df)
        rows_validated = validation_report["rows_passed"]
        print(f"[pipeline] Validation passed {rows_validated} rows.")

        # Incremental filter (CRDS-24)
        incremental_df, incremental_from = filter_new_records(validated_df, engine)
        rows_loaded = len(incremental_df)

        if rows_loaded == 0:
            print("[pipeline] No new records to load. Pipeline complete.")
            log_load_history(
                engine,
                rows_extracted=rows_extracted,
                rows_after_validation=rows_validated,
                rows_transformed=rows_transformed,
                rows_loaded=0,
                incremental_from=incremental_from,
                status="success",
            )
            return

        # Load (CRDS-26: idempotent via ON CONFLICT)
        load_staging_data(incremental_df, engine)
        populate_dimensions_and_fact(engine)

        # Record history (CRDS-23)
        log_load_history(
            engine,
            rows_extracted=rows_extracted,
            rows_after_validation=rows_validated,
            rows_transformed=rows_transformed,
            rows_loaded=rows_loaded,
            incremental_from=incremental_from,
            status="success",
        )

        print(f"[pipeline] ETL pipeline completed. {rows_loaded} rows loaded.")

    except Exception as exc:
        print(f"[pipeline] Pipeline failed: {exc}", file=sys.stderr)
        log_load_history(
            engine,
            rows_extracted=rows_extracted,
            rows_after_validation=rows_validated,
            rows_transformed=rows_transformed,
            rows_loaded=rows_loaded,
            incremental_from=incremental_from,
            status="failed",
            error_message=str(exc),
        )
        raise


if __name__ == "__main__":
    run_pipeline()
