from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from vibe_bt_03.data_ingestion.errors import IngestionValidationError
from vibe_bt_03.data_ingestion.normalizers.common import (
    base_code, first_value, infer_future_exchange, infer_stock_exchange,
    normalize_provider, parse_optional_date, stock_symbol)
from vibe_bt_03.database.api.types import AssetInput, InstrumentInput
from vibe_bt_03.database.models.enums import (AssetClass, AssetStatus,
                                              InstrumentInfoLevel,
                                              InstrumentStatus)


def normalize_stock_instruments(
    provider: str,
    records: Sequence[Mapping[str, Any]],
) -> tuple[list[AssetInput], list[InstrumentInput]]:
    normalize_provider(provider)
    assets: list[AssetInput] = []
    instruments: list[InstrumentInput] = []

    for record in records:
        raw_symbol = first_value(record, "ts_code", "symbol", "code", "证券代码", "代码")
        if raw_symbol is None:
            raise IngestionValidationError("stock instrument symbol is required")

        exchange = infer_stock_exchange(str(raw_symbol))
        symbol = stock_symbol(str(raw_symbol), exchange)
        code = base_code(symbol)
        name = first_value(record, "name", "名称", "security_name")
        listed_date = parse_optional_date(first_value(record, "list_date", "上市日期"))
        delisted_date = parse_optional_date(first_value(record, "delist_date", "退市日期"))
        status = _stock_status(first_value(record, "list_status", "状态"))

        assets.append(
            AssetInput(
                asset_class=AssetClass.STOCK,
                code=code,
                exchange=exchange,
                name=str(name) if name is not None else None,
                status=_asset_status(status),
                listed_date=listed_date,
                delisted_date=delisted_date,
                extra=dict(record),
            )
        )
        instruments.append(
            InstrumentInput(
                symbol=symbol,
                asset_class=AssetClass.STOCK,
                info_level=InstrumentInfoLevel.BASIC,
                asset_code=code,
                exchange=exchange,
                name=str(name) if name is not None else None,
                status=status,
                listed_date=listed_date,
                delisted_date=delisted_date,
                extra=dict(record),
            )
        )

    return assets, instruments


def normalize_future_instruments(
    provider: str,
    records: Sequence[Mapping[str, Any]],
) -> tuple[list[AssetInput], list[InstrumentInput]]:
    normalize_provider(provider)
    assets: list[AssetInput] = []
    instruments: list[InstrumentInput] = []

    for record in records:
        raw_symbol = first_value(record, "ts_code", "symbol", "code", "合约代码", "代码")
        if raw_symbol is None:
            raise IngestionValidationError("future instrument symbol is required")

        symbol = str(raw_symbol).strip().upper()
        code = base_code(symbol)
        exchange = infer_future_exchange(symbol, first_value(record, "exchange", "交易所"))
        name = first_value(record, "name", "名称", "合约名称")
        listed_date = parse_optional_date(first_value(record, "list_date", "上市日期"))
        delisted_date = parse_optional_date(first_value(record, "delist_date", "到期日期", "退市日期"))
        status = InstrumentStatus.EXPIRED if delisted_date is not None else InstrumentStatus.ACTIVE

        assets.append(
            AssetInput(
                asset_class=AssetClass.FUTURE,
                code=code,
                exchange=exchange,
                name=str(name) if name is not None else None,
                status=_asset_status(status),
                listed_date=listed_date,
                delisted_date=delisted_date,
                extra=dict(record),
            )
        )
        instruments.append(
            InstrumentInput(
                symbol=symbol,
                asset_class=AssetClass.FUTURE,
                info_level=InstrumentInfoLevel.BASIC,
                asset_code=code,
                exchange=exchange,
                name=str(name) if name is not None else None,
                status=status,
                listed_date=listed_date,
                delisted_date=delisted_date,
                extra=dict(record),
            )
        )

    return assets, instruments


def _stock_status(raw_status: Any) -> InstrumentStatus:
    if raw_status is None:
        return InstrumentStatus.ACTIVE
    normalized = str(raw_status).strip().upper()
    if normalized in {"L", "上市", "ACTIVE", "NORMAL"}:
        return InstrumentStatus.ACTIVE
    if normalized in {"D", "退市", "DELISTED"}:
        return InstrumentStatus.DELISTED
    return InstrumentStatus.SUSPENDED


def _asset_status(status: InstrumentStatus) -> AssetStatus:
    if status == InstrumentStatus.DELISTED:
        return AssetStatus.DELISTED
    if status == InstrumentStatus.ACTIVE:
        return AssetStatus.ACTIVE
    return AssetStatus.INACTIVE
