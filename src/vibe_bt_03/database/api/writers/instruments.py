from __future__ import annotations

from collections.abc import Sequence

from vibe_bt_03.database.api.types import AssetInput, InstrumentInput, SaveResult
from vibe_bt_03.database.repositories.instruments import AssetRepository, InstrumentRepository
from vibe_bt_03.database.session import session_scope


def save_assets(items: Sequence[AssetInput], *, overwrite: bool = True) -> SaveResult:
    """Save standardized asset metadata from ingestion."""

    with session_scope() as session:
        return AssetRepository(session).upsert_many(items, overwrite=overwrite)


def save_instruments(items: Sequence[InstrumentInput], *, overwrite: bool = True) -> SaveResult:
    """Save standardized instrument metadata from ingestion."""

    with session_scope() as session:
        return InstrumentRepository(session).upsert_many(items, overwrite=overwrite)
