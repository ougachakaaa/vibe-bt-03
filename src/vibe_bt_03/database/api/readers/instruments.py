from __future__ import annotations

from vibe_bt_03.database.api.types import AssetView, InstrumentView
from vibe_bt_03.database.models.enums import AssetClass, Exchange, InstrumentStatus
from vibe_bt_03.database.repositories.instruments import (
    AssetRepository,
    InstrumentRepository,
    to_asset_view,
    to_instrument_view,
)
from vibe_bt_03.database.session import session_scope


def get_instrument(symbol: str) -> InstrumentView | None:
    """Load one instrument by symbol."""

    with session_scope() as session:
        instrument = InstrumentRepository(session).get_by_symbol(symbol)
        return to_instrument_view(instrument) if instrument is not None else None


def list_instruments(
    *,
    asset_class: AssetClass | None = None,
    exchange: Exchange | None = None,
    status: InstrumentStatus | None = None,
) -> list[InstrumentView]:
    """List instruments using stable view objects instead of ORM models."""

    with session_scope() as session:
        instruments = InstrumentRepository(session).list(
            asset_class=asset_class,
            exchange=exchange,
            status=status,
        )
        return [to_instrument_view(instrument) for instrument in instruments]


def list_assets(
    *,
    asset_class: AssetClass | None = None,
    exchange: Exchange | None = None,
) -> list[AssetView]:
    """List asset metadata using stable view objects instead of ORM models."""

    with session_scope() as session:
        assets = AssetRepository(session).list(asset_class=asset_class, exchange=exchange)
        return [to_asset_view(asset) for asset in assets]
