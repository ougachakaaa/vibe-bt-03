from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from vibe_bt_03.database.api.types import SaveResult, StockDailyBarInput
from vibe_bt_03.database.api.writers.market_data import save_stock_raw_bars


class StockDailyBarSource(Protocol):
    def fetch_daily_bars(
        self,
        symbol: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[StockDailyBarInput]:
        """Fetch standardized stock daily bars for one instrument."""


SaveStockRawBars = Callable[
    [str, Sequence[StockDailyBarInput]],
    SaveResult,
]


@dataclass(frozen=True)
class SyncStockRawBarsResult:
    symbol: str
    fetched: int
    saved: SaveResult
    source: str | None = None


@dataclass(frozen=True)
class SyncStockRawBarsUseCase:
    source: StockDailyBarSource
    save_bars: SaveStockRawBars = save_stock_raw_bars
    source_name: str | None = None

    def execute(
        self,
        symbol: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> SyncStockRawBarsResult:
        bars = self.source.fetch_daily_bars(
            symbol,
            start_date=start_date,
            end_date=end_date,
        )
        save_result = self.save_bars(symbol, bars)

        return SyncStockRawBarsResult(
            symbol=symbol,
            fetched=len(bars),
            saved=save_result,
            source=self.source_name,
        )

