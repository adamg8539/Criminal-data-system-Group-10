"""Create the permanent PostgreSQL tables configured in .env."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etl.load import get_db_engine  # noqa: E402


def setup_database():
    schema_sql = (PROJECT_ROOT / "database" / "schema.sql").read_text(
        encoding="utf-8"
    )

    engine = get_db_engine()
    with engine.begin() as connection:
        connection.exec_driver_sql(schema_sql)

    print("[setup_db] Database schema created successfully.")


if __name__ == "__main__":
    setup_database()
