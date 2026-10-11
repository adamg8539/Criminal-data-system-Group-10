from unittest.mock import MagicMock

import pandas as pd

from etl.load import STAGING_COLUMNS, load_data_atomic


def test_atomic_load_uses_temp_staging_and_updates_fact_conflicts():
    df = pd.DataFrame(
        [["2026-06-01", "Sydney", "Greater Sydney", "Assault", "Assault", "Violent", 42]],
        columns=STAGING_COLUMNS,
    )
    engine = MagicMock()
    connection = engine.begin.return_value.__enter__.return_value
    cursor = connection.connection.driver_connection.cursor.return_value

    rows_loaded = load_data_atomic(df, engine)

    assert rows_loaded == 1
    engine.begin.assert_called_once_with()
    sql_statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    assert "CREATE TEMP TABLE staging_crime" in sql_statements[0]
    assert "ON COMMIT DROP" in sql_statements[0]
    assert "DO UPDATE SET incident_count = EXCLUDED.incident_count" in sql_statements[-1]

    copy_sql, _ = cursor.copy_expert.call_args.args
    assert "COPY staging_crime" in copy_sql
    cursor.close.assert_called_once_with()
