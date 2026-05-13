from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from vibe_bt_03.data_ingestion.errors import IngestionValidationError
from vibe_bt_03.data_ingestion.normalizers import (normalize_stock_daily_bars,
                                                   normalize_stock_instruments)
from vibe_bt_03.data_ingestion.validators import validate_stock_daily_bars
from vibe_bt_03.database.models.enums import AssetClass, Exchange


def test_normalize_stock_instruments_from_tushare_record() -> None:
    assets, instruments = normalize_stock_instruments(
        "tushare",
        [{"ts_code": "000001.SZ", "name": "平安银行", "list_date": "19910403", "list_status": "L"}],
    )

    assert assets[0].asset_class == AssetClass.STOCK
    assert assets[0].code == "000001"
    assert instruments[0].symbol == "000001.SZ"
    assert instruments[0].exchange == Exchange.SZSE
    assert instruments[0].listed_date == date(1991, 4, 3)


def test_normalize_stock_daily_bars_from_tushare_record() -> None:
    bars = normalize_stock_daily_bars(
        "tushare",
        [{"trade_date": "20240102", "open": "10", "high": "11", "low": "9", "close": "10.5"}],
    )

    assert bars[0].trade_date == date(2024, 1, 2)
    assert bars[0].open == Decimal("10")
    assert bars[0].source == "tushare"


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(IngestionValidationError, match="unsupported provider"):
        normalize_stock_daily_bars("csv", [])


def test_validate_stock_daily_bars_rejects_invalid_ohlc() -> None:
    bars = normalize_stock_daily_bars(
        "akshare",
        [{"日期": "2024-01-02", "开盘": "10", "最高": "9", "最低": "8", "收盘": "10"}],
    )

    with pytest.raises(IngestionValidationError, match="high price"):
        validate_stock_daily_bars(bars)
