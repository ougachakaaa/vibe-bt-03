from __future__ import annotations

from collections.abc import Iterable

from vibe_bt_03.data_ingestion.errors import IngestionValidationError
from vibe_bt_03.database.api.types import AssetInput, InstrumentInput


def validate_assets(items: Iterable[AssetInput]) -> list[AssetInput]:
    assets = list(items)
    for item in assets:
        if not item.code.strip():
            raise IngestionValidationError("asset code must not be empty")
        if item.asset_class is None:
            raise IngestionValidationError("asset asset_class is required")
    return assets


def validate_instruments(items: Iterable[InstrumentInput]) -> list[InstrumentInput]:
    instruments = list(items)
    for item in instruments:
        if not item.symbol.strip():
            raise IngestionValidationError("instrument symbol must not be empty")
        if item.asset_class is None:
            raise IngestionValidationError("instrument asset_class is required")
    return instruments
