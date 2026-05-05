from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from vibe_bt_03.database.models.base import Base, TimestampMixin, enum_type
from vibe_bt_03.database.models.enums import CalendarSessionType, Exchange


class Calendar(TimestampMixin, Base):
    """Exchange trading calendar used to validate daily market data."""

    __tablename__ = "calendar"
    __table_args__ = (
        UniqueConstraint("exchange", "trade_date", name="uq_calendar_exchange_trade_date"),
        Index("ix_calendar_trade_date", "trade_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange: Mapped[Exchange] = mapped_column(enum_type(Exchange), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, nullable=False)
    session_type: Mapped[CalendarSessionType] = mapped_column(
        enum_type(CalendarSessionType),
        default=CalendarSessionType.FULL,
        nullable=False,
    )
    prev_trade_date: Mapped[date | None] = mapped_column(Date)
    next_trade_date: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(String(255))
