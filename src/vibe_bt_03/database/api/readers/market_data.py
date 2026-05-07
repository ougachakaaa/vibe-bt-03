from __future__ import annotations

from datetime import date

from vibe_bt_03.database.api.types import FutureDailyBarView, StockDailyBarView
from vibe_bt_03.database.models.enums import AdjustmentType
from vibe_bt_03.database.repositories.bars import (
    BarRepository,
    to_future_bar_view,
    to_stock_adjusted_bar_view,
    to_stock_raw_bar_view,
)
from vibe_bt_03.database.session import session_scope


def load_stock_raw_bars(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[StockDailyBarView]:
    """Load unadjusted stock bars for quant/backtest callers."""

    with session_scope() as session:
        bars = BarRepository(session).list_stock_raw(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        return [to_stock_raw_bar_view(bar) for bar in bars]


def load_stock_adjusted_bars(
    symbol: str,
    adjustment_type: AdjustmentType,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[StockDailyBarView]:
    """Load adjusted stock bars for quant/backtest callers."""

    with session_scope() as session:
        bars = BarRepository(session).list_stock_adjusted(
            symbol=symbol,
            adjustment_type=adjustment_type,
            start_date=start_date,
            end_date=end_date,
        )
        return [to_stock_adjusted_bar_view(bar) for bar in bars]


def load_future_bars(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
    *,
    main_contract_only: bool = False,
) -> list[FutureDailyBarView]:
    """Load futures bars for quant/backtest callers."""

    with session_scope() as session:
        bars = BarRepository(session).list_future(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            main_contract_only=main_contract_only,
        )
        return [to_future_bar_view(bar) for bar in bars]
