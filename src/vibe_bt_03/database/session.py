from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy.orm import Session, sessionmaker

from vibe_bt_03.database.engine import get_engine


_active_session: ContextVar[Session | None] = ContextVar("active_database_session", default=None)
_session_factory: sessionmaker[Session] | None = None


def get_session_factory() -> sessionmaker[Session]:
    """Return the configured session factory."""

    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
    return _session_factory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a session and manage commit/rollback for top-level callers."""

    existing_session = _active_session.get()
    if existing_session is not None:
        yield existing_session
        return

    session = get_session_factory()()
    token = _active_session.set(session)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        _active_session.reset(token)
        session.close()


@contextmanager
def database_transaction() -> Iterator[None]:
    """Group multiple database API calls into one transaction without exposing Session."""

    with session_scope():
        yield


def clear_session_factory() -> None:
    """Clear cached session factory after engine reconfiguration."""

    global _session_factory
    _session_factory = None
