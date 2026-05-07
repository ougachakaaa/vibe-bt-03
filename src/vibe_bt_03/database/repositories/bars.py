from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select

from vibe_bt_03.database.api.types import (
    FutureDailyBarInput,
    FutureDailyBarView,
    SaveResult,
    StockAdjustedBarInput,
    StockDailyBarInput,
    StockDailyBarView,
)
from vibe_bt_03.database.errors import DatabaseLookupError
from vibe_bt_03.database.models.bar import BarFuture, BarStockAdjusted, BarStockRaw
from vibe_bt_03.database.models.enums import AdjustmentType
from vibe_bt_03.database.models.instrument import Instrument
from vibe_bt_03.database.repositories.base import BaseRepository, validate_price_bar
from vibe_bt_03.database.repositories.instruments import InstrumentRepository


class BarRepository(BaseRepository):
    def require_instrument(self, symbol: str) -> Instrument:
        instrument = InstrumentRepository(self.session).get_by_symbol(symbol)
        if instrument is None:
            raise DatabaseLookupError(f"instrument not found: {symbol}")
        return instrument

    def list_stock_raw(
        self,
        *,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[BarStockRaw]:
        stmt = (
            select(BarStockRaw)
            .join(BarStockRaw.instrument)
            .where(Instrument.symbol == symbol.strip())
            .order_by(BarStockRaw.trade_date)
        )
        if start_date is not None:
            stmt = stmt.where(BarStockRaw.trade_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(BarStockRaw.trade_date <= end_date)
        return list(self.session.scalars(stmt))

    def list_stock_adjusted(
        self,
        *,
        symbol: str,
        adjustment_type: AdjustmentType,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[BarStockAdjusted]:
        stmt = (
            select(BarStockAdjusted)
            .join(BarStockAdjusted.instrument)
            .where(
                Instrument.symbol == symbol.strip(),
                BarStockAdjusted.adjustment_type == adjustment_type,
            )
            .order_by(BarStockAdjusted.trade_date)
        )
        if start_date is not None:
            stmt = stmt.where(BarStockAdjusted.trade_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(BarStockAdjusted.trade_date <= end_date)
        return list(self.session.scalars(stmt))

    def list_future(
        self,
        *,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
        main_contract_only: bool = False,
    ) -> list[BarFuture]:
        stmt = (
            select(BarFuture)
            .join(BarFuture.instrument)
            .where(Instrument.symbol == symbol.strip())
            .order_by(BarFuture.trade_date)
        )
        if start_date is not None:
            stmt = stmt.where(BarFuture.trade_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(BarFuture.trade_date <= end_date)
        if main_contract_only:
            stmt = stmt.where(BarFuture.is_main_contract.is_(True))
        return list(self.session.scalars(stmt))

    def upsert_stock_raw(
        self,
        symbol: str,
        bars: Sequence[StockDailyBarInput],
        *,
        source: str | None = None,
        overwrite: bool = True,
    ) -> SaveResult:
        instrument = self.require_instrument(symbol)
        inserted = 0
        updated = 0

        for item in bars:
            validate_price_bar(item.open, item.high, item.low, item.close)
            existing = self.session.scalar(
                select(BarStockRaw).where(
                    BarStockRaw.instrument_id == instrument.id,
                    BarStockRaw.trade_date == item.trade_date,
                )
            )
            values = {
                "instrument_id": instrument.id,
                "trade_date": item.trade_date,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
                "amount": item.amount,
                "source": source or item.source,
                "pre_close": item.pre_close,
                "turnover_rate": item.turnover_rate,
                "limit_up": item.limit_up,
                "limit_down": item.limit_down,
                "is_suspended": item.is_suspended,
            }
            if existing is None:
                self.session.add(BarStockRaw(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(existing, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(bars) - inserted - updated)

    def upsert_stock_adjusted(
        self,
        symbol: str,
        adjustment_type: AdjustmentType,
        bars: Sequence[StockAdjustedBarInput],
        *,
        source: str | None = None,
        overwrite: bool = True,
    ) -> SaveResult:
        instrument = self.require_instrument(symbol)
        inserted = 0
        updated = 0

        for item in bars:
            validate_price_bar(item.open, item.high, item.low, item.close)
            raw_trade_date = item.raw_bar_trade_date or item.trade_date
            raw_bar = self.session.scalar(
                select(BarStockRaw).where(
                    BarStockRaw.instrument_id == instrument.id,
                    BarStockRaw.trade_date == raw_trade_date,
                )
            )
            existing = self.session.scalar(
                select(BarStockAdjusted).where(
                    BarStockAdjusted.instrument_id == instrument.id,
                    BarStockAdjusted.trade_date == item.trade_date,
                    BarStockAdjusted.adjustment_type == adjustment_type,
                )
            )
            values = {
                "instrument_id": instrument.id,
                "raw_bar_id": raw_bar.id if raw_bar is not None else None,
                "trade_date": item.trade_date,
                "adjustment_type": adjustment_type,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
                "amount": item.amount,
                "source": source or item.source,
                "pre_close": item.pre_close,
                "adjustment_factor": item.adjustment_factor,
            }
            if existing is None:
                self.session.add(BarStockAdjusted(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(existing, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(bars) - inserted - updated)

    def upsert_future(
        self,
        symbol: str,
        bars: Sequence[FutureDailyBarInput],
        *,
        source: str | None = None,
        overwrite: bool = True,
    ) -> SaveResult:
        instrument = self.require_instrument(symbol)
        inserted = 0
        updated = 0

        for item in bars:
            validate_price_bar(item.open, item.high, item.low, item.close)
            existing = self.session.scalar(
                select(BarFuture).where(
                    BarFuture.instrument_id == instrument.id,
                    BarFuture.trade_date == item.trade_date,
                )
            )
            values = {
                "instrument_id": instrument.id,
                "trade_date": item.trade_date,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
                "amount": item.amount,
                "source": source or item.source,
                "settlement": item.settlement,
                "pre_settlement": item.pre_settlement,
                "open_interest": item.open_interest,
                "pre_open_interest": item.pre_open_interest,
                "change_open_interest": item.change_open_interest,
                "upper_limit": item.upper_limit,
                "lower_limit": item.lower_limit,
                "is_main_contract": item.is_main_contract,
            }
            if existing is None:
                self.session.add(BarFuture(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(existing, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(bars) - inserted - updated)


def to_stock_raw_bar_view(bar: BarStockRaw) -> StockDailyBarView:
    return StockDailyBarView(
        symbol=bar.instrument.symbol,
        trade_date=bar.trade_date,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        volume=bar.volume,
        amount=bar.amount,
        source=bar.source,
        pre_close=bar.pre_close,
        turnover_rate=bar.turnover_rate,
        limit_up=bar.limit_up,
        limit_down=bar.limit_down,
        is_suspended=bar.is_suspended,
    )


def to_stock_adjusted_bar_view(bar: BarStockAdjusted) -> StockDailyBarView:
    return StockDailyBarView(
        symbol=bar.instrument.symbol,
        trade_date=bar.trade_date,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        volume=bar.volume,
        amount=bar.amount,
        source=bar.source,
        pre_close=bar.pre_close,
        adjustment_type=bar.adjustment_type,
        adjustment_factor=bar.adjustment_factor,
    )


def to_future_bar_view(bar: BarFuture) -> FutureDailyBarView:
    return FutureDailyBarView(
        symbol=bar.instrument.symbol,
        trade_date=bar.trade_date,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        volume=bar.volume,
        amount=bar.amount,
        source=bar.source,
        settlement=bar.settlement,
        pre_settlement=bar.pre_settlement,
        open_interest=bar.open_interest,
        pre_open_interest=bar.pre_open_interest,
        change_open_interest=bar.change_open_interest,
        upper_limit=bar.upper_limit,
        lower_limit=bar.lower_limit,
        is_main_contract=bar.is_main_contract,
    )
