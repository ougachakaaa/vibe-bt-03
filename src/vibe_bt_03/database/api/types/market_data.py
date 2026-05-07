from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from vibe_bt_03.database.models.enums import AdjustmentType


@dataclass(frozen=True)
class StockDailyBarInput:
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None
    amount: Decimal | None = None
    source: str | None = None
    pre_close: Decimal | None = None
    turnover_rate: Decimal | None = None
    limit_up: Decimal | None = None
    limit_down: Decimal | None = None
    is_suspended: bool = False


@dataclass(frozen=True)
class StockAdjustedBarInput:
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjustment_factor: Decimal
    volume: Decimal | None = None
    amount: Decimal | None = None
    source: str | None = None
    pre_close: Decimal | None = None
    raw_bar_trade_date: date | None = None


@dataclass(frozen=True)
class FutureDailyBarInput:
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None
    amount: Decimal | None = None
    source: str | None = None
    settlement: Decimal | None = None
    pre_settlement: Decimal | None = None
    open_interest: Decimal | None = None
    pre_open_interest: Decimal | None = None
    change_open_interest: Decimal | None = None
    upper_limit: Decimal | None = None
    lower_limit: Decimal | None = None
    is_main_contract: bool = False


@dataclass(frozen=True)
class StockDailyBarView:
    symbol: str
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None
    amount: Decimal | None
    source: str | None
    pre_close: Decimal | None = None
    turnover_rate: Decimal | None = None
    limit_up: Decimal | None = None
    limit_down: Decimal | None = None
    is_suspended: bool | None = None
    adjustment_type: AdjustmentType | None = None
    adjustment_factor: Decimal | None = None


@dataclass(frozen=True)
class FutureDailyBarView:
    symbol: str
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None
    amount: Decimal | None
    source: str | None
    settlement: Decimal | None
    pre_settlement: Decimal | None
    open_interest: Decimal | None
    pre_open_interest: Decimal | None
    change_open_interest: Decimal | None
    upper_limit: Decimal | None
    lower_limit: Decimal | None
    is_main_contract: bool
