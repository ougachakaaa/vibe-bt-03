from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select

from vibe_bt_03.database.api.types import CalendarSessionInput, CalendarSessionView, SaveResult
from vibe_bt_03.database.models.calendar import Calendar
from vibe_bt_03.database.models.enums import Exchange
from vibe_bt_03.database.repositories.base import BaseRepository


class CalendarRepository(BaseRepository):
    def list_sessions(
        self,
        *,
        exchange: Exchange,
        start_date: date,
        end_date: date,
        open_only: bool = False,
    ) -> list[Calendar]:
        stmt = (
            select(Calendar)
            .where(
                Calendar.exchange == exchange,
                Calendar.trade_date >= start_date,
                Calendar.trade_date <= end_date,
            )
            .order_by(Calendar.trade_date)
        )
        if open_only:
            stmt = stmt.where(Calendar.is_open.is_(True))
        return list(self.session.scalars(stmt))

    def upsert_many(
        self,
        items: Sequence[CalendarSessionInput],
        *,
        overwrite: bool = True,
    ) -> SaveResult:
        inserted = 0
        updated = 0

        for item in items:
            stmt = select(Calendar).where(
                Calendar.exchange == item.exchange,
                Calendar.trade_date == item.trade_date,
            )
            calendar = self.session.scalar(stmt)
            values = {
                "exchange": item.exchange,
                "trade_date": item.trade_date,
                "is_open": item.is_open,
                "session_type": item.session_type,
                "prev_trade_date": item.prev_trade_date,
                "next_trade_date": item.next_trade_date,
                "note": item.note,
            }

            if calendar is None:
                self.session.add(Calendar(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(calendar, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(items) - inserted - updated)


def to_calendar_session_view(calendar: Calendar) -> CalendarSessionView:
    return CalendarSessionView(
        exchange=calendar.exchange,
        trade_date=calendar.trade_date,
        is_open=calendar.is_open,
        session_type=calendar.session_type,
        prev_trade_date=calendar.prev_trade_date,
        next_trade_date=calendar.next_trade_date,
        note=calendar.note,
    )
