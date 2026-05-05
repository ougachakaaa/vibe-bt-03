from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vibe_bt_03.database.models.base import Base, TimestampMixin, enum_type
from vibe_bt_03.database.models.enums import AdjustmentType

if TYPE_CHECKING:
    from vibe_bt_03.database.models.instrument import Instrument


class DailyPriceMixin:
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    source: Mapped[str | None] = mapped_column(String(64))


class BarStockRaw(DailyPriceMixin, TimestampMixin, Base):
    """Unadjusted stock daily bars as published by the data source."""

    __tablename__ = "bar_stock_raw"
    __table_args__ = (
        UniqueConstraint("instrument_id", "trade_date", name="uq_bar_stock_raw_instrument_date"),
        CheckConstraint("high >= low", name="high_gte_low"),
        Index("ix_bar_stock_raw_trade_date", "trade_date"),
        Index("ix_bar_stock_raw_instrument_date", "instrument_id", "trade_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instrument.id"), nullable=False)
    pre_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    turnover_rate: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    limit_up: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    limit_down: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    instrument: Mapped[Instrument] = relationship("Instrument", back_populates="stock_raw_bars")
    adjusted_bars: Mapped[list[BarStockAdjusted]] = relationship(
        "BarStockAdjusted",
        back_populates="raw_bar",
    )


class BarStockAdjusted(DailyPriceMixin, TimestampMixin, Base):
    """Adjusted stock daily bars for research and backtest calculations."""

    __tablename__ = "bar_stock_adjusted"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "trade_date",
            "adjustment_type",
            name="uq_bar_stock_adjusted_instrument_date_type",
        ),
        CheckConstraint("high >= low", name="high_gte_low"),
        Index("ix_bar_stock_adjusted_trade_date", "trade_date"),
        Index("ix_bar_stock_adjusted_instrument_date", "instrument_id", "trade_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_bar_id: Mapped[int | None] = mapped_column(ForeignKey("bar_stock_raw.id"))
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instrument.id"), nullable=False)
    adjustment_type: Mapped[AdjustmentType] = mapped_column(enum_type(AdjustmentType), nullable=False)
    pre_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    adjustment_factor: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)

    instrument: Mapped[Instrument] = relationship("Instrument", back_populates="stock_adjusted_bars")
    raw_bar: Mapped[BarStockRaw | None] = relationship("BarStockRaw", back_populates="adjusted_bars")


class BarFuture(DailyPriceMixin, TimestampMixin, Base):
    """Futures daily bars, preserving settlement and open-interest fields."""

    __tablename__ = "bar_future"
    __table_args__ = (
        UniqueConstraint("instrument_id", "trade_date", name="uq_bar_future_instrument_date"),
        CheckConstraint("high >= low", name="high_gte_low"),
        Index("ix_bar_future_trade_date", "trade_date"),
        Index("ix_bar_future_instrument_date", "instrument_id", "trade_date"),
        Index("ix_bar_future_main_contract", "trade_date", "is_main_contract"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instrument.id"), nullable=False)
    settlement: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    pre_settlement: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    open_interest: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    pre_open_interest: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    change_open_interest: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    upper_limit: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    lower_limit: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    is_main_contract: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    instrument: Mapped[Instrument] = relationship("Instrument", back_populates="future_bars")
