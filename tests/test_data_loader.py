from unittest.mock import MagicMock

import pandas as pd

from app import data_loader


def test_load_data_reads_rds_once_and_caches_result(monkeypatch):
    expected = pd.DataFrame({"date": [pd.Timestamp("2026-06-01")], "incident_count": [42]})
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    read_sql_query = MagicMock(return_value=expected)

    monkeypatch.setattr(data_loader, "get_db_engine", lambda: engine)
    monkeypatch.setattr(data_loader.pd, "read_sql_query", read_sql_query)
    data_loader._cache = None

    first = data_loader.load_data()
    second = data_loader.load_data()

    assert first is expected
    assert second is expected
    engine.connect.assert_called_once_with()
    read_sql_query.assert_called_once_with(
        data_loader.DATA_QUERY,
        connection,
        parse_dates=["date"],
    )
    engine.dispose.assert_called_once_with()
