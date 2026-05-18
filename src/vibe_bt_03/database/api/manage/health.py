from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from vibe_bt_03.database.engine import get_engine


@dataclass(frozen=True)
class DatabaseHealth:
    ok: bool
    dialect: str | None = None
    driver: str | None = None
    url_masked: str | None = None
    error: str | None = None


def get_database_health() -> DatabaseHealth:
    """Return database connectivity details for admin and CLI callers."""

    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        return DatabaseHealth(
            ok=True,
            dialect=engine.dialect.name,
            driver=engine.dialect.driver,
            url_masked=engine.url.render_as_string(hide_password=True),
        )
    except Exception as exc:
        return DatabaseHealth(ok=False, error=f"{type(exc).__name__}: {exc}")


def check_database_connection() -> bool:
    """Return True when the configured database accepts a simple query."""

    return get_database_health().ok
