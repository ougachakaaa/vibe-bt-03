from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from vibe_bt_03.database.models.enums import (
    AssetClass,
    AssetStatus,
    Exchange,
    InstrumentInfoLevel,
    InstrumentStatus,
)


@dataclass(frozen=True)
class AssetInput:
    asset_class: AssetClass
    code: str
    exchange: Exchange | None = None
    name: str | None = None
    status: AssetStatus | None = None
    listed_date: date | None = None
    delisted_date: date | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class InstrumentInput:
    symbol: str
    asset_class: AssetClass | None = None
    info_level: InstrumentInfoLevel = InstrumentInfoLevel.IDENTITY_ONLY
    asset_code: str | None = None
    exchange: Exchange | None = None
    name: str | None = None
    status: InstrumentStatus | None = None
    listed_date: date | None = None
    delisted_date: date | None = None
    price_tick: Decimal | None = None
    multiplier: Decimal | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class AssetView:
    code: str
    asset_class: AssetClass
    exchange: Exchange | None
    name: str | None
    status: AssetStatus | None
    listed_date: date | None
    delisted_date: date | None
    extra: dict[str, Any]


@dataclass(frozen=True)
class InstrumentView:
    symbol: str
    asset_class: AssetClass | None
    info_level: InstrumentInfoLevel
    exchange: Exchange | None
    name: str | None
    status: InstrumentStatus | None
    listed_date: date | None
    delisted_date: date | None
    price_tick: Decimal | None
    multiplier: Decimal | None
    extra: dict[str, Any]
    asset_code: str | None = None
