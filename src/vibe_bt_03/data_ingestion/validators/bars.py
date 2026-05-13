from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from vibe_bt_03.data_ingestion.errors import IngestionValidationError
from vibe_bt_03.database.api.types import (FutureDailyBarInput,
                                           StockDailyBarInput)


def validate_stock_daily_bars(items: Iterable[StockDailyBarInput]) -> list[StockDailyBarInput]:
    bars = list(items)
    for item in bars:
        _validate_ohlc(item.open, item.high, item.low, item.close)
    return bars


def validate_future_daily_bars(items: Iterable[FutureDailyBarInput]) -> list[FutureDailyBarInput]:
    bars = list(items)
    for item in bars:
        _validate_ohlc(item.open, item.high, item.low, item.close)
    return bars


def _validate_ohlc(open_: Decimal, high: Decimal, low: Decimal, close: Decimal) -> None:
    if min(open_, high, low, close) < 0:
        raise IngestionValidationError("OHLC prices must be non-negative")
    if high < low:
        raise IngestionValidationError("high price must be greater than or equal to low price")
    if high < open_ or high < close:
        raise IngestionValidationError("high price must be greater than or equal to open and close")
    if low > open_ or low > close:
        raise IngestionValidationError("low price must be less than or equal to open and close")
