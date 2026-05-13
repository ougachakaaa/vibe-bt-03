from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import SecretStr

from vibe_bt_03.config import get_settings
from vibe_bt_03.data_ingestion.sources.base import RawRecords
from vibe_bt_03.database.models.enums import AdjustmentType


@dataclass(frozen=True)
class TushareSource:
    token: SecretStr | str | None = None
    source_name: str = "tushare"

    def resolved_token(self) -> str | None:
        token = self.token if self.token is not None else get_settings().datasource.tushare_token
        if isinstance(token, SecretStr):
            return token.get_secret_value()
        return token

    def client(self) -> Any:
        raise NotImplementedError("TushareSource.client is not implemented yet")

    def fetch_stock_instrument_records(self, symbol: str) -> RawRecords:
        raise NotImplementedError("Tushare stock instrument fetching is not implemented yet")

    def fetch_future_instrument_records(self, symbol: str) -> RawRecords:
        raise NotImplementedError("Tushare future instrument fetching is not implemented yet")

    def fetch_stock_raw_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Tushare stock raw bar fetching is not implemented yet")

    def fetch_stock_adjusted_bar_records(
        self,
        symbol: str,
        adjustment_type: AdjustmentType,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Tushare stock adjusted bar fetching is not implemented yet")

    def fetch_future_bar_records(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RawRecords:
        raise NotImplementedError("Tushare future bar fetching is not implemented yet")
