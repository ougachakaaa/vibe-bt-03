from __future__ import annotations

from collections.abc import Sequence

from vibe_bt_03.database.api.types import (
    FutureDailyBarInput,
    SaveResult,
    StockAdjustedBarInput,
    StockDailyBarInput,
)
from vibe_bt_03.database.models.enums import AdjustmentType
from vibe_bt_03.database.repositories.bars import BarRepository
from vibe_bt_03.database.session import session_scope


def save_stock_raw_bars(
    symbol: str,
    bars: Sequence[StockDailyBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
) -> SaveResult:
    """Save unadjusted stock daily bars for one instrument."""

    with session_scope() as session:
        return BarRepository(session).upsert_stock_raw(
            symbol,
            bars,
            source=source,
            overwrite=overwrite,
        )


def save_stock_adjusted_bars(
    symbol: str,
    adjustment_type: AdjustmentType,
    bars: Sequence[StockAdjustedBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
) -> SaveResult:
    """Save adjusted stock daily bars for one instrument and adjustment type."""

    with session_scope() as session:
        return BarRepository(session).upsert_stock_adjusted(
            symbol,
            adjustment_type,
            bars,
            source=source,
            overwrite=overwrite,
        )


def save_future_bars(
    symbol: str,
    bars: Sequence[FutureDailyBarInput],
    *,
    source: str | None = None,
    overwrite: bool = True,
) -> SaveResult:
    """Save futures daily bars for one instrument."""

    with session_scope() as session:
        return BarRepository(session).upsert_future(
            symbol,
            bars,
            source=source,
            overwrite=overwrite,
        )
