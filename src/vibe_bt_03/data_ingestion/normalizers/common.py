from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from vibe_bt_03.data_ingestion.errors import IngestionValidationError
from vibe_bt_03.database.models.enums import Exchange

SUPPORTED_PROVIDERS = {"tushare", "akshare"}
MISSING_VALUES = {"", "--", "None", "none", "nan", "NaN", "NAN", "null", "NULL"}


def normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_PROVIDERS:
        raise IngestionValidationError(f"unsupported provider: {provider}")
    return normalized


def first_value(record: dict[str, Any] | Any, *keys: str) -> Any:
    for key in keys:
        if key in record:
            value = record[key]
            if value is not None and str(value) not in MISSING_VALUES:
                return value
    return None


def parse_date(value: Any, *, field_name: str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if value is None or str(value) in MISSING_VALUES:
        raise IngestionValidationError(f"{field_name} is required")

    text = str(value).strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise IngestionValidationError(f"{field_name} has invalid date format: {value}")


def parse_optional_date(value: Any) -> date | None:
    if value is None or str(value) in MISSING_VALUES:
        return None
    return parse_date(value, field_name="date")


def parse_decimal(value: Any, *, field_name: str, required: bool = True) -> Decimal | None:
    if value is None or str(value) in MISSING_VALUES:
        if required:
            raise IngestionValidationError(f"{field_name} is required")
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except (InvalidOperation, ValueError) as exc:
        raise IngestionValidationError(f"{field_name} has invalid decimal value: {value}") from exc


def parse_bool(value: Any, *, default: bool = False) -> bool:
    if value is None or str(value) in MISSING_VALUES:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "停牌", "suspended"}


def infer_stock_exchange(code_or_symbol: str) -> Exchange | None:
    symbol = code_or_symbol.strip().upper()
    if symbol.endswith((".SH", ".SSE")):
        return Exchange.SSE
    if symbol.endswith((".SZ", ".SZSE")):
        return Exchange.SZSE
    if symbol.endswith((".BJ", ".BSE")):
        return Exchange.BSE
    code = symbol.split(".", 1)[0]
    if code.startswith(("60", "68", "90")):
        return Exchange.SSE
    if code.startswith(("00", "30", "20")):
        return Exchange.SZSE
    if code.startswith(("43", "83", "87", "88", "92")):
        return Exchange.BSE
    return None


def infer_future_exchange(symbol: str, raw_exchange: Any = None) -> Exchange | None:
    if raw_exchange is not None and str(raw_exchange).strip():
        raw = str(raw_exchange).strip().upper()
        aliases = {
            "CFFEX": Exchange.CFFEX,
            "SHFE": Exchange.SHFE,
            "DCE": Exchange.DCE,
            "CZCE": Exchange.CZCE,
            "GFEX": Exchange.GFEX,
        }
        if raw in aliases:
            return aliases[raw]

    suffix = symbol.strip().upper().split(".")[-1] if "." in symbol else ""
    return {
        "CFX": Exchange.CFFEX,
        "CFFEX": Exchange.CFFEX,
        "SHF": Exchange.SHFE,
        "SHFE": Exchange.SHFE,
        "DCE": Exchange.DCE,
        "ZCE": Exchange.CZCE,
        "CZCE": Exchange.CZCE,
        "GFE": Exchange.GFEX,
        "GFEX": Exchange.GFEX,
    }.get(suffix)


def stock_symbol(code_or_symbol: str, exchange: Exchange | None = None) -> str:
    raw = code_or_symbol.strip().upper()
    if "." in raw:
        code, suffix = raw.split(".", 1)
        suffix = {"SH": "SH", "SSE": "SH", "SZ": "SZ", "SZSE": "SZ", "BJ": "BJ", "BSE": "BJ"}.get(
            suffix,
            suffix,
        )
        return f"{code}.{suffix}"

    resolved_exchange = exchange or infer_stock_exchange(raw)
    suffix = {
        Exchange.SSE: "SH",
        Exchange.SZSE: "SZ",
        Exchange.BSE: "BJ",
    }.get(resolved_exchange)
    return f"{raw}.{suffix}" if suffix else raw


def base_code(symbol: str) -> str:
    return symbol.strip().upper().split(".", 1)[0]
