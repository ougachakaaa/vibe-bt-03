from __future__ import annotations

from datetime import date
from decimal import Decimal

from vibe_bt_03.database.api.types import SaveResult, StockDailyBarInput
from vibe_bt_03.use_cases.data_ingestion import SyncStockRawBarsUseCase


class FakeStockDailyBarSource:
    def fetch_daily_bars(
        self,
        symbol: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[StockDailyBarInput]:
        assert symbol == "000001.SZ"
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 31)
        return [
            StockDailyBarInput(
                trade_date=date(2024, 1, 2),
                open=Decimal("10"),
                high=Decimal("11"),
                low=Decimal("9"),
                close=Decimal("10.5"),
            )
        ]


def test_sync_stock_raw_bars_use_case_fetches_and_saves_bars() -> None:
    saved_symbols: list[str] = []

    def save_bars(symbol: str, bars: list[StockDailyBarInput]) -> SaveResult:
        saved_symbols.append(symbol)
        assert len(bars) == 1
        return SaveResult(inserted=1)

    use_case = SyncStockRawBarsUseCase(
        source=FakeStockDailyBarSource(),
        save_bars=save_bars,
        source_name="fake",
    )

    result = use_case.execute(
        "000001.SZ",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
    )

    assert saved_symbols == ["000001.SZ"]
    assert result.symbol == "000001.SZ"
    assert result.fetched == 1
    assert result.saved.inserted == 1
    assert result.source == "fake"

