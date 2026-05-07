from __future__ import annotations

from datetime import date

from vibe_bt_03.database.api.types import CalendarSessionView
from vibe_bt_03.database.models.enums import Exchange
from vibe_bt_03.database.repositories.calendars import CalendarRepository, to_calendar_session_view
from vibe_bt_03.database.session import session_scope


def load_calendar_sessions(
    exchange: Exchange,
    start_date: date,
    end_date: date,
    *,
    open_only: bool = False,
) -> list[CalendarSessionView]:
    """Load exchange calendar sessions for a date range."""

    with session_scope() as session:
        sessions = CalendarRepository(session).list_sessions(
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            open_only=open_only,
        )
        return [to_calendar_session_view(item) for item in sessions]
