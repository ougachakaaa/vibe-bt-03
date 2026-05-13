from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from vibe_bt_03.data_ingestion import workflows
from vibe_bt_03.data_ingestion.batching import batched
from vibe_bt_03.data_ingestion.workflows import (
    ingest_stock_raw_bars, ingest_stock_raw_bars_from_provider,
    ingest_stock_raw_bars_from_source)
from vibe_bt_03.database.api.types import SaveResult, StockDailyBarInput


def make_bar(day: int) -> StockDailyBarInput:
    value = Decimal(day)
    return StockDailyBarInput(
        trade_date=date(2024, 1, day),
        open=value,
        high=value,
        low=value,
        close=value,
    )


def test_batched_splits_items() -> None:
    assert list(batched([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]


def test_ingest_stock_raw_bars_dry_run_skips_writer(monkeypatch) -> None:
    called = False

    def fake_save_stock_raw_bars(*args, **kwargs) -> SaveResult:
        nonlocal called
        called = True
        return SaveResult(inserted=1)

    monkeypatch.setattr(workflows, "save_stock_raw_bars", fake_save_stock_raw_bars)

    result = ingest_stock_raw_bars("000001.SZ", [make_bar(1)], source="test", dry_run=True)

    assert not called
    assert result.dataset == "stock_raw_bars:000001.SZ"
    assert result.source == "test"
    assert result.fetched == 1
    assert result.standardized == 1
    assert result.persisted == 0
    assert result.dry_run


def test_ingest_stock_raw_bars_merges_batch_results(monkeypatch) -> None:
    batches: list[tuple[StockDailyBarInput, ...]] = []

    def fake_save_stock_raw_bars(symbol, bars, *, source=None, overwrite=True) -> SaveResult:
        assert symbol == "000001.SZ"
        assert source == "test"
        assert overwrite is False
        batch = tuple(bars)
        batches.append(batch)
        return SaveResult(inserted=len(batch))

    monkeypatch.setattr(workflows, "save_stock_raw_bars", fake_save_stock_raw_bars)

    result = ingest_stock_raw_bars(
        "000001.SZ",
        [make_bar(1), make_bar(2), make_bar(3)],
        source="test",
        overwrite=False,
        batch_size=2,
        dry_run=False,
    )

    assert [len(batch) for batch in batches] == [2, 1]
    assert result.inserted == 3
    assert result.updated == 0
    assert result.skipped == 0
    assert result.persisted == 3


@dataclass
class FakeStockBarSource:
    source_name: str = "fake"

    def fetch_stock_raw_bars(self, symbol, start_date=None, end_date=None):
        assert symbol == "000001.SZ"
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 2)
        return [make_bar(1), make_bar(2)]

    def fetch_stock_adjusted_bars(self, symbol, adjustment_type, start_date=None, end_date=None):
        raise NotImplementedError


def test_ingest_stock_raw_bars_from_source(monkeypatch) -> None:
    def fake_save_stock_raw_bars(symbol, bars, *, source=None, overwrite=True) -> SaveResult:
        assert source == "fake"
        return SaveResult(inserted=len(bars))

    monkeypatch.setattr(workflows, "save_stock_raw_bars", fake_save_stock_raw_bars)

    result = ingest_stock_raw_bars_from_source(
        FakeStockBarSource(),
        "000001.SZ",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
        dry_run=False,
    )

    assert result.source == "fake"
    assert result.fetched == 2
    assert result.persisted == 2


@dataclass
class FakeProviderSource:
    source_name: str = "tushare"

    def fetch_stock_instrument_records(self, symbol):
        raise NotImplementedError

    def fetch_future_instrument_records(self, symbol):
        raise NotImplementedError

    def fetch_stock_raw_bar_records(self, symbol, start_date=None, end_date=None):
        assert symbol == "000001.SZ"
        return [
            {
                "trade_date": "20240101",
                "open": "10",
                "high": "11",
                "low": "9",
                "close": "10.5",
                "vol": "100",
            }
        ]

    def fetch_stock_adjusted_bar_records(self, symbol, adjustment_type, start_date=None, end_date=None):
        raise NotImplementedError

    def fetch_future_bar_records(self, symbol, start_date=None, end_date=None):
        raise NotImplementedError


def test_ingest_stock_raw_bars_from_provider_normalizes_and_writes(monkeypatch) -> None:
    resolver_calls: list[str] = []

    class FakeResolver:
        def __init__(self, source):
            self.source = source

        def ensure_stock_instrument(self, symbol, *, dry_run=None, overwrite=True):
            resolver_calls.append(symbol)
            return None

    def fake_save_stock_raw_bars(symbol, bars, *, source=None, overwrite=True) -> SaveResult:
        assert symbol == "000001.SZ"
        assert source == "tushare"
        assert bars[0].trade_date == date(2024, 1, 1)
        return SaveResult(inserted=len(bars))

    monkeypatch.setattr(workflows, "InstrumentResolver", FakeResolver)
    monkeypatch.setattr(workflows, "save_stock_raw_bars", fake_save_stock_raw_bars)

    result = ingest_stock_raw_bars_from_provider(FakeProviderSource(), "000001.SZ", dry_run=False)

    assert resolver_calls == ["000001.SZ"]
    assert result.provider == "tushare"
    assert result.ensured_instruments == 1
    assert result.persisted == 1
