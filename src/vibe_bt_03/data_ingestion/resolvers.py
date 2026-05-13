from __future__ import annotations

from dataclasses import dataclass

from vibe_bt_03.config import get_settings
from vibe_bt_03.data_ingestion.errors import IngestionLookupError
from vibe_bt_03.data_ingestion.normalizers import (
    normalize_future_instruments, normalize_stock_instruments)
from vibe_bt_03.data_ingestion.sources import ProviderSource
from vibe_bt_03.data_ingestion.validators import (validate_assets,
                                                  validate_instruments)
from vibe_bt_03.database.api.readers.instruments import get_instrument
from vibe_bt_03.database.api.types import InstrumentView
from vibe_bt_03.database.api.writers.instruments import (save_assets,
                                                         save_instruments)


@dataclass(frozen=True)
class InstrumentResolver:
    source: ProviderSource

    def ensure_stock_instrument(
        self,
        symbol: str,
        *,
        dry_run: bool | None = None,
        overwrite: bool = True,
    ) -> InstrumentView | None:
        return self._ensure_instrument(
            symbol,
            fetch=lambda: self.source.fetch_stock_instrument_records(symbol),
            normalize=lambda records: normalize_stock_instruments(self.source.source_name, records),
            dry_run=dry_run,
            overwrite=overwrite,
        )

    def ensure_future_instrument(
        self,
        symbol: str,
        *,
        dry_run: bool | None = None,
        overwrite: bool = True,
    ) -> InstrumentView | None:
        return self._ensure_instrument(
            symbol,
            fetch=lambda: self.source.fetch_future_instrument_records(symbol),
            normalize=lambda records: normalize_future_instruments(self.source.source_name, records),
            dry_run=dry_run,
            overwrite=overwrite,
        )

    def _ensure_instrument(self, symbol, *, fetch, normalize, dry_run, overwrite):
        existing = get_instrument(symbol)
        if existing is not None:
            return existing

        records = fetch()
        if not records:
            raise IngestionLookupError(f"instrument metadata not found: {symbol}")

        assets, instruments = normalize(records)
        assets = validate_assets(assets)
        instruments = validate_instruments(instruments)
        if not instruments:
            raise IngestionLookupError(f"instrument metadata not found: {symbol}")
        if dry_run is None:
            dry_run = get_settings().ingestion.dry_run
        if dry_run:
            return None

        save_assets(assets, overwrite=overwrite)
        save_instruments(instruments, overwrite=overwrite)

        resolved = get_instrument(symbol)
        if resolved is None:
            resolved = get_instrument(instruments[0].symbol)
        if resolved is None:
            raise IngestionLookupError(f"instrument could not be resolved after save: {symbol}")
        return resolved


def ensure_stock_instrument(
    symbol: str,
    source: ProviderSource,
    *,
    dry_run: bool | None = None,
    overwrite: bool = True,
) -> InstrumentView | None:
    return InstrumentResolver(source).ensure_stock_instrument(symbol, dry_run=dry_run, overwrite=overwrite)


def ensure_future_instrument(
    symbol: str,
    source: ProviderSource,
    *,
    dry_run: bool | None = None,
    overwrite: bool = True,
) -> InstrumentView | None:
    return InstrumentResolver(source).ensure_future_instrument(symbol, dry_run=dry_run, overwrite=overwrite)
