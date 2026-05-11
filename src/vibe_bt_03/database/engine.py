from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine

from vibe_bt_03.config import DatabaseSettings
from vibe_bt_03.database.errors import DatabaseNotConfiguredError


_engine: Engine | None = None


def configure_database(
    settings: DatabaseSettings | str | None = None,
    *,
    database_url: str | None = None,
    **engine_options: Any,
) -> Engine:
    """Configure the process-wide SQLAlchemy engine used by database APIs."""

    global _engine

    if database_url is not None:
        resolved_url = database_url
    elif isinstance(settings, DatabaseSettings):
        resolved_url = settings.url
        engine_options.setdefault("echo", settings.echo)
    else:
        resolved_url = settings

    if not resolved_url:
        raise DatabaseNotConfiguredError(
            "database settings or URL is required; pass DatabaseSettings from get_settings().database"
        )

    _engine = create_engine(resolved_url, future=True, **engine_options)
    return _engine


def get_engine() -> Engine:
    """Return the configured engine."""

    if _engine is None:
        return configure_database()
    return _engine


def dispose_engine() -> None:
    """Dispose the configured engine and clear process-wide database state."""

    global _engine

    if _engine is not None:
        _engine.dispose()
    _engine = None
