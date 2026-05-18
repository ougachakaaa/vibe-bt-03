from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from vibe_bt_03.config import DatabaseSettings
from vibe_bt_03.database.engine import configure_database as _configure_database
from vibe_bt_03.database.engine import dispose_engine
from vibe_bt_03.database.session import clear_session_factory
from vibe_bt_03.database.session import database_transaction as _database_transaction


def configure_database(
    settings: DatabaseSettings | str | None = None,
    *,
    database_url: str | None = None,
    **engine_options: Any,
) -> None:
    """Configure database connectivity for API callers and CLI tools."""

    dispose_engine()
    clear_session_factory()
    _configure_database(settings, database_url=database_url, **engine_options)


def dispose_database() -> None:
    """Close database connections and clear cached session state."""

    dispose_engine()
    clear_session_factory()


@contextmanager
def database_transaction() -> Iterator[None]:
    """Group multiple database API calls into one transaction."""

    with _database_transaction():
        yield
