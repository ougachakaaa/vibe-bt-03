from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any, Protocol

from vibe_bt_03.database.api.types import (AssetInput, CalendarSessionInput,
                                           FutureDailyBarInput,
                                           InstrumentInput,
                                           StockAdjustedBarInput,
                                           StockDailyBarInput)
from vibe_bt_03.database.models.enums import AdjustmentType, Exchange

RawRecord = Mapping[str, Any]
RawRecords = Sequence[RawRecord]


class DataSource(Protocol):
    source_name: str


class InstrumentSource(DataSource, Protocol):
    def fetch_assets(self) -> Sequence[AssetInput]: ...

    def fetch_instruments(self) -> Sequence[InstrumentInput]: ...


class CalendarSource(DataSource, Protocol):
    def fetch_calendar_sessions(
        self,
        exchange: Exchange,
        start_date: date,
        end_date: date,
    ) -> Sequence[CalendarSessionInput]: ...


class StockBarSource(DataSource, Protocol):
    def fetch_stock_raw_bars(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[StockDailyBarInput]: ...

    def fetch_stock_adjusted_bars(
        self,
        symbol: str,
        adjustment_type: AdjustmentType,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[StockAdjustedBarInput]: ...


class FutureBarSource(DataSource, Protocol):
    def fetch_future_bars(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[FutureDailyBarInput]: ...


class ProviderSource(DataSource, Protocol):
    def fetch_stock_instrument_records(self, symbol: str) -> RawRecords: ...

    def fetch_future_instrument_records(self, symbol: str) -> RawRecords: ...

    def fetch_stock_raw_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords: ...

    def fetch_stock_adjusted_bar_records(
        self,
        symbol: str,
        adjustment_type: AdjustmentType,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords: ...

    def fetch_future_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords: ...
