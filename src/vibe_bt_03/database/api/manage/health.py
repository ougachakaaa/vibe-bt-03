from __future__ import annotations

from sqlalchemy import text

from vibe_bt_03.database.engine import get_engine


def check_database_connection() -> bool:
    """Return True when the configured database accepts a simple query."""

    try:
        with get_engine().connect() as connection:
            connection.execute(text("select 1"))
        return True
    except Exception:
        return False
