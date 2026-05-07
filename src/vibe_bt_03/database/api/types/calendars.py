from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from vibe_bt_03.database.models.enums import CalendarSessionType, Exchange


@dataclass(frozen=True)
class CalendarSessionInput:
    exchange: Exchange
    trade_date: date
    is_open: bool
    session_type: CalendarSessionType = CalendarSessionType.FULL
    prev_trade_date: date | None = None
    next_trade_date: date | None = None
    note: str | None = None


@dataclass(frozen=True)
class CalendarSessionView:
    exchange: Exchange
    trade_date: date
    is_open: bool
    session_type: CalendarSessionType
    prev_trade_date: date | None
    next_trade_date: date | None
    note: str | None
