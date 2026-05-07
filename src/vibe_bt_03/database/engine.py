from __future__ import annotations

import os
from typing import Any

from sqlalchemy import Engine, create_engine

from vibe_bt_03.database.errors import DatabaseNotConfiguredError


DATABASE_URL_ENV = "VIBE_BT_DATABASE_URL"

_engine: Engine | None = None


def configure_database(database_url: str | None = None, **engine_options: Any) -> Engine:
    """Configure the process-wide SQLAlchemy engine used by database APIs."""

    global _engine

    resolved_url = database_url or os.getenv(DATABASE_URL_ENV)
    if not resolved_url:
        raise DatabaseNotConfiguredError(
            f"database URL is required; pass one explicitly or set {DATABASE_URL_ENV}"
        )

    _engine = create_engine(resolved_url, future=True, **engine_options)
    return _engine


def get_engine() -> Engine:
    """Return the configured engine, lazily reading VIBE_BT_DATABASE_URL if needed."""

    if _engine is None:
        return configure_database()
    return _engine


def dispose_engine() -> None:
    """Dispose the configured engine and clear process-wide database state."""

    global _engine

    if _engine is not None:
        _engine.dispose()
    _engine = None
