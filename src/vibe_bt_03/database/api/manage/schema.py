from __future__ import annotations

from vibe_bt_03.database.engine import get_engine
from vibe_bt_03.database.models import Base


def create_all_tables() -> None:
    """Create all SQLAlchemy metadata tables."""

    Base.metadata.create_all(get_engine())


def drop_all_tables() -> None:
    """Drop all SQLAlchemy metadata tables."""

    Base.metadata.drop_all(get_engine())


def reset_database() -> None:
    """Drop and recreate all SQLAlchemy metadata tables."""

    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
