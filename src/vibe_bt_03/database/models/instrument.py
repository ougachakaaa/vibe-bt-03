from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vibe_bt_03.database.models.base import Base, TimestampMixin, enum_type
from vibe_bt_03.database.models.enums import (
    AssetClass,
    AssetStatus,
    Exchange,
    InstrumentInfoLevel,
    InstrumentStatus,
)

if TYPE_CHECKING:
    from vibe_bt_03.database.models.bar import BarFuture, BarStockAdjusted, BarStockRaw


class Asset(TimestampMixin, Base):
    """Asset-level identity, such as an A-share company or a futures product."""

    __tablename__ = "asset"
    __table_args__ = (
        UniqueConstraint("asset_class", "code", "exchange", name="uq_asset_class_code_exchange"),
        CheckConstraint("code <> ''", name="code_not_empty"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_class: Mapped[AssetClass] = mapped_column(enum_type(AssetClass), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange: Mapped[Exchange | None] = mapped_column(enum_type(Exchange))
    name: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[AssetStatus | None] = mapped_column(enum_type(AssetStatus))
    listed_date: Mapped[date | None] = mapped_column(Date)
    delisted_date: Mapped[date | None] = mapped_column(Date)
    extra: Mapped[dict[str, object]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    instruments: Mapped[list[Instrument]] = relationship("Instrument", back_populates="asset")


class Instrument(TimestampMixin, Base):
    """Smallest common tradable identity shared by stocks and futures."""

    __tablename__ = "instrument"
    __table_args__ = (
        UniqueConstraint("symbol", name="uq_instrument_symbol"),
        CheckConstraint("symbol <> ''", name="symbol_not_empty"),
        Index("ix_instrument_asset_class_exchange", "asset_class", "exchange"),
        Index("ix_instrument_info_level", "info_level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    asset_class: Mapped[AssetClass | None] = mapped_column(enum_type(AssetClass))
    info_level: Mapped[InstrumentInfoLevel] = mapped_column(
        enum_type(InstrumentInfoLevel),
        default=InstrumentInfoLevel.IDENTITY_ONLY,
        nullable=False,
    )

    asset_id: Mapped[int | None] = mapped_column(ForeignKey("asset.id"))
    exchange: Mapped[Exchange | None] = mapped_column(enum_type(Exchange))
    name: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[InstrumentStatus | None] = mapped_column(enum_type(InstrumentStatus))
    listed_date: Mapped[date | None] = mapped_column(Date)
    delisted_date: Mapped[date | None] = mapped_column(Date)
    price_tick: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    multiplier: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    extra: Mapped[dict[str, object]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    asset: Mapped[Asset | None] = relationship("Asset", back_populates="instruments")
    stock_raw_bars: Mapped[list[BarStockRaw]] = relationship("BarStockRaw", back_populates="instrument")
    stock_adjusted_bars: Mapped[list[BarStockAdjusted]] = relationship(
        "BarStockAdjusted",
        back_populates="instrument",
    )
    future_bars: Mapped[list[BarFuture]] = relationship("BarFuture", back_populates="instrument")
