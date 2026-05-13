from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import date
from typing import TypeVar

from vibe_bt_03.config import get_settings
from vibe_bt_03.data_ingestion.batching import batched, materialize
from vibe_bt_03.data_ingestion.normalizers import (normalize_future_daily_bars,
                                                   normalize_stock_daily_bars)
from vibe_bt_03.data_ingestion.resolvers import InstrumentResolver
from vibe_bt_03.data_ingestion.results import IngestionResult
from vibe_bt_03.data_ingestion.sources import (CalendarSource, FutureBarSource,
                                               InstrumentSource,
                                               ProviderSource, StockBarSource)
from vibe_bt_03.data_ingestion.validators import (validate_future_daily_bars,
                                                  validate_stock_daily_bars)
from vibe_bt_03.database.api.types import (AssetInput, CalendarSessionInput,
                                           FutureDailyBarInput,
                                           InstrumentInput, SaveResult,
                                           StockAdjustedBarInput,
                                           StockDailyBarInput)
from vibe_bt_03.database.api.writers.calendars import save_calendar_sessions
from vibe_bt_03.database.api.writers.instruments import (save_assets,
                                                         save_instruments)
from vibe_bt_03.database.api.writers.market_data import (
    save_future_bars, save_stock_adjusted_bars, save_stock_raw_bars)
from vibe_bt_03.database.models.enums import AdjustmentType, Exchange

T = TypeVar("T")
SimpleWriter = Callable[[Sequence[T]], SaveResult]


def _resolve_dry_run(dry_run: bool | None) -> bool:
    if dry_run is not None:
        return dry_run
    return get_settings().ingestion.dry_run


def _resolve_batch_size(batch_size: int | None) -> int:
    if batch_size is not None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
        return batch_size
    return get_settings().ingestion.stock_bar_batch_size


def _save_items(
    *,
    dataset: str,
    items: Iterable[T] | Sequence[T],
    writer: SimpleWriter[T],
    source: str | None = None,
    provider: str | None = None,
    batch_size: int | None = None,
    dry_run: bool | None = None,
    ensured_instruments: int = 0,
) -> IngestionResult:
    standardized = materialize(items)
    is_dry_run = _resolve_dry_run(dry_run)
    if is_dry_run:
        return IngestionResult(
            dataset=dataset,
            source=source,
            provider=provider,
            fetched=len(standardized),
            standardized=len(standardized),
            dry_run=True,
            ensured_instruments=ensured_instruments,
        )

    result = SaveResult()
    for batch in batched(standardized, _resolve_batch_size(batch_size)):
        result = result.merge(writer(batch))

    return IngestionResult(
        dataset=dataset,
        source=source,
        provider=provider,
        fetched=len(standardized),
        standardized=len(standardized),
        saved=result,
        ensured_instruments=ensured_instruments,
    )


def ingest_assets(
    items: Iterable[AssetInput] | Sequence[AssetInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset="assets",
        items=items,
        writer=lambda batch: save_assets(batch, overwrite=overwrite),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_instruments(
    items: Iterable[InstrumentInput] | Sequence[InstrumentInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset="instruments",
        items=items,
        writer=lambda batch: save_instruments(batch, overwrite=overwrite),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_calendar_sessions(
    items: Iterable[CalendarSessionInput] | Sequence[CalendarSessionInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset="calendar_sessions",
        items=items,
        writer=lambda batch: save_calendar_sessions(batch, overwrite=overwrite),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_stock_raw_bars(
    symbol: str,
    bars: Iterable[StockDailyBarInput] | Sequence[StockDailyBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset=f"stock_raw_bars:{symbol}",
        items=bars,
        writer=lambda batch: save_stock_raw_bars(symbol, batch, source=source, overwrite=overwrite),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_stock_adjusted_bars(
    symbol: str,
    adjustment_type: AdjustmentType,
    bars: Iterable[StockAdjustedBarInput] | Sequence[StockAdjustedBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset=f"stock_adjusted_bars:{symbol}:{adjustment_type.value}",
        items=bars,
        writer=lambda batch: save_stock_adjusted_bars(
            symbol,
            adjustment_type,
            batch,
            source=source,
            overwrite=overwrite,
        ),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_future_bars(
    symbol: str,
    bars: Iterable[FutureDailyBarInput] | Sequence[FutureDailyBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return _save_items(
        dataset=f"future_bars:{symbol}",
        items=bars,
        writer=lambda batch: save_future_bars(symbol, batch, source=source, overwrite=overwrite),
        source=source,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_assets_from_source(
    source: InstrumentSource,
    *,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_assets(
        source.fetch_assets(),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_instruments_from_source(
    source: InstrumentSource,
    *,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_instruments(
        source.fetch_instruments(),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_calendar_sessions_from_source(
    source: CalendarSource,
    exchange: Exchange,
    start_date: date,
    end_date: date,
    *,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_calendar_sessions(
        source.fetch_calendar_sessions(exchange, start_date, end_date),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_stock_raw_bars_from_source(
    source: StockBarSource,
    symbol: str,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_stock_raw_bars(
        symbol,
        source.fetch_stock_raw_bars(symbol, start_date, end_date),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_stock_adjusted_bars_from_source(
    source: StockBarSource,
    symbol: str,
    adjustment_type: AdjustmentType,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_stock_adjusted_bars(
        symbol,
        adjustment_type,
        source.fetch_stock_adjusted_bars(symbol, adjustment_type, start_date, end_date),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_future_bars_from_source(
    source: FutureBarSource,
    symbol: str,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> IngestionResult:
    return ingest_future_bars(
        symbol,
        source.fetch_future_bars(symbol, start_date, end_date),
        source=source.source_name,
        overwrite=overwrite,
        batch_size=batch_size,
        dry_run=dry_run,
    )


def ingest_stock_raw_bars_from_provider(
    source: ProviderSource,
    symbol: str,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
    ensure_instrument: bool = True,
) -> IngestionResult:
    records = source.fetch_stock_raw_bar_records(symbol, start_date, end_date)
    bars = validate_stock_daily_bars(normalize_stock_daily_bars(source.source_name, records))
    ensured_instruments = 0
    if ensure_instrument:
        InstrumentResolver(source).ensure_stock_instrument(symbol, dry_run=dry_run, overwrite=overwrite)
        ensured_instruments = 1

    return _save_items(
        dataset=f"stock_raw_bars:{symbol}",
        items=bars,
        writer=lambda batch: save_stock_raw_bars(symbol, batch, source=source.source_name, overwrite=overwrite),
        source=source.source_name,
        provider=source.source_name,
        batch_size=batch_size,
        dry_run=dry_run,
        ensured_instruments=ensured_instruments,
    )


def ingest_future_bars_from_provider(
    source: ProviderSource,
    symbol: str,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    overwrite: bool = True,
    batch_size: int | None = None,
    dry_run: bool | None = None,
    ensure_instrument: bool = True,
) -> IngestionResult:
    records = source.fetch_future_bar_records(symbol, start_date, end_date)
    bars = validate_future_daily_bars(normalize_future_daily_bars(source.source_name, records))
    ensured_instruments = 0
    if ensure_instrument:
        InstrumentResolver(source).ensure_future_instrument(symbol, dry_run=dry_run, overwrite=overwrite)
        ensured_instruments = 1

    return _save_items(
        dataset=f"future_bars:{symbol}",
        items=bars,
        writer=lambda batch: save_future_bars(symbol, batch, source=source.source_name, overwrite=overwrite),
        source=source.source_name,
        provider=source.source_name,
        batch_size=batch_size,
        dry_run=dry_run,
        ensured_instruments=ensured_instruments,
    )
