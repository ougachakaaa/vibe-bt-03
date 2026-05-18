from __future__ import annotations

from sqlalchemy import inspect

from vibe_bt_03.database.api import (
    configure_database,
    create_all_tables,
    drop_all_tables,
    reset_database,
)
from vibe_bt_03.database.engine import get_engine


def _table_names() -> set[str]:
    return set(inspect(get_engine()).get_table_names())


def test_create_all_tables_creates_model_tables() -> None:
    configure_database("sqlite+pysqlite:///:memory:")

    create_all_tables()

    assert {
        "asset",
        "bar_future",
        "bar_stock_adjusted",
        "bar_stock_raw",
        "calendar",
        "instrument",
    }.issubset(_table_names())


def test_drop_all_tables_removes_model_tables() -> None:
    configure_database("sqlite+pysqlite:///:memory:")
    create_all_tables()

    drop_all_tables()

    assert _table_names() == set()


def test_reset_database_recreates_model_tables() -> None:
    configure_database("sqlite+pysqlite:///:memory:")
    create_all_tables()
    drop_all_tables()

    reset_database()

    assert "instrument" in _table_names()
