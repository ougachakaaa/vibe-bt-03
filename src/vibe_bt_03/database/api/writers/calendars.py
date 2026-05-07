from __future__ import annotations

from collections.abc import Sequence

from vibe_bt_03.database.api.types import CalendarSessionInput, SaveResult
from vibe_bt_03.database.repositories.calendars import CalendarRepository
from vibe_bt_03.database.session import session_scope


def save_calendar_sessions(
    items: Sequence[CalendarSessionInput],
    *,
    overwrite: bool = True,
) -> SaveResult:
    """Save standardized exchange calendar sessions from ingestion."""

    with session_scope() as session:
        return CalendarRepository(session).upsert_many(items, overwrite=overwrite)
