from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from vibe_bt_03.database.api.types import (
    AssetInput,
    AssetView,
    InstrumentInput,
    InstrumentView,
    SaveResult,
)
from vibe_bt_03.database.errors import DatabaseValidationError
from vibe_bt_03.database.models.enums import AssetClass, Exchange, InstrumentStatus
from vibe_bt_03.database.models.instrument import Asset, Instrument
from vibe_bt_03.database.repositories.base import BaseRepository


class AssetRepository(BaseRepository):
    def get(
        self,
        asset_class: AssetClass,
        code: str,
        exchange: Exchange | None,
    ) -> Asset | None:
        stmt = select(Asset).where(
            Asset.asset_class == asset_class,
            Asset.code == code,
            Asset.exchange == exchange,
        )
        return self.session.scalar(stmt)

    def upsert_many(self, items: Sequence[AssetInput], *, overwrite: bool = True) -> SaveResult:
        inserted = 0
        updated = 0

        for item in items:
            code = item.code.strip()
            if not code:
                raise DatabaseValidationError("asset code must not be empty")

            asset = self.get(item.asset_class, code, item.exchange)
            values = {
                "asset_class": item.asset_class,
                "code": code,
                "exchange": item.exchange,
                "name": item.name,
                "status": item.status,
                "listed_date": item.listed_date,
                "delisted_date": item.delisted_date,
                "extra": item.extra or {},
            }

            if asset is None:
                self.session.add(Asset(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(asset, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(items) - inserted - updated)

    def list(
        self,
        *,
        asset_class: AssetClass | None = None,
        exchange: Exchange | None = None,
    ) -> list[Asset]:
        stmt = select(Asset).order_by(Asset.asset_class, Asset.exchange, Asset.code)
        if asset_class is not None:
            stmt = stmt.where(Asset.asset_class == asset_class)
        if exchange is not None:
            stmt = stmt.where(Asset.exchange == exchange)
        return list(self.session.scalars(stmt))


class InstrumentRepository(BaseRepository):
    def get_by_symbol(self, symbol: str) -> Instrument | None:
        stmt = (
            select(Instrument)
            .options(joinedload(Instrument.asset))
            .where(Instrument.symbol == symbol.strip())
        )
        return self.session.scalar(stmt)

    def list(
        self,
        *,
        asset_class: AssetClass | None = None,
        exchange: Exchange | None = None,
        status: InstrumentStatus | None = None,
    ) -> list[Instrument]:
        stmt = (
            select(Instrument)
            .options(joinedload(Instrument.asset))
            .order_by(Instrument.asset_class, Instrument.exchange, Instrument.symbol)
        )
        if asset_class is not None:
            stmt = stmt.where(Instrument.asset_class == asset_class)
        if exchange is not None:
            stmt = stmt.where(Instrument.exchange == exchange)
        if status is not None:
            stmt = stmt.where(Instrument.status == status)
        return list(self.session.scalars(stmt))

    def upsert_many(self, items: Sequence[InstrumentInput], *, overwrite: bool = True) -> SaveResult:
        inserted = 0
        updated = 0
        asset_repo = AssetRepository(self.session)

        for item in items:
            symbol = item.symbol.strip()
            if not symbol:
                raise DatabaseValidationError("instrument symbol must not be empty")

            instrument = self.get_by_symbol(symbol)
            asset_id = None
            if item.asset_code and item.asset_class:
                asset = asset_repo.get(item.asset_class, item.asset_code.strip(), item.exchange)
                if asset is not None:
                    asset_id = asset.id

            values = {
                "symbol": symbol,
                "asset_class": item.asset_class,
                "info_level": item.info_level,
                "asset_id": asset_id,
                "exchange": item.exchange,
                "name": item.name,
                "status": item.status,
                "listed_date": item.listed_date,
                "delisted_date": item.delisted_date,
                "price_tick": item.price_tick,
                "multiplier": item.multiplier,
                "extra": item.extra or {},
            }

            if instrument is None:
                self.session.add(Instrument(**values))
                inserted += 1
            elif overwrite:
                for field, value in values.items():
                    setattr(instrument, field, value)
                updated += 1

        self.session.flush()
        return SaveResult(inserted=inserted, updated=updated, skipped=len(items) - inserted - updated)


def to_asset_view(asset: Asset) -> AssetView:
    return AssetView(
        code=asset.code,
        asset_class=asset.asset_class,
        exchange=asset.exchange,
        name=asset.name,
        status=asset.status,
        listed_date=asset.listed_date,
        delisted_date=asset.delisted_date,
        extra=dict(asset.extra or {}),
    )


def to_instrument_view(instrument: Instrument) -> InstrumentView:
    return InstrumentView(
        symbol=instrument.symbol,
        asset_class=instrument.asset_class,
        info_level=instrument.info_level,
        exchange=instrument.exchange,
        name=instrument.name,
        status=instrument.status,
        listed_date=instrument.listed_date,
        delisted_date=instrument.delisted_date,
        price_tick=instrument.price_tick,
        multiplier=instrument.multiplier,
        extra=dict(instrument.extra or {}),
        asset_code=instrument.asset.code if instrument.asset is not None else None,
    )
