from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from vibe_bt_03.data_ingestion.sources.base import RawRecords
from vibe_bt_03.database.models.enums import AdjustmentType


@dataclass(frozen=True)
class AkshareSource:
    source_name: str = "akshare"

    def fetch_stock_instrument_records(self, symbol: str) -> RawRecords:
        raise NotImplementedError("Akshare stock instrument fetching is not implemented yet")

    def fetch_future_instrument_records(self, symbol: str) -> RawRecords:
        raise NotImplementedError("Akshare future instrument fetching is not implemented yet")

    def fetch_stock_raw_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Akshare stock raw bar fetching is not implemented yet")

    def fetch_stock_adjusted_bar_records(
        self,
        symbol: str,
        adjustment_type: AdjustmentType,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Akshare stock adjusted bar fetching is not implemented yet")

    def fetch_future_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Akshare future bar fetching is not implemented yet")
