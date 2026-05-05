from __future__ import annotations

from enum import StrEnum


class AssetClass(StrEnum):
    STOCK = "stock"
    FUTURE = "future"


class Exchange(StrEnum):
    SSE = "SSE"
    SZSE = "SZSE"
    BSE = "BSE"
    CFFEX = "CFFEX"
    SHFE = "SHFE"
    DCE = "DCE"
    CZCE = "CZCE"
    GFEX = "GFEX"


class AssetStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELISTED = "delisted"


class InstrumentStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    DELISTED = "delisted"


class InstrumentInfoLevel(StrEnum):
    IDENTITY_ONLY = "identity_only"
    CLASSIFIED = "classified"
    BASIC = "basic"
    COMPLETE = "complete"


class CalendarSessionType(StrEnum):
    FULL = "full"
    HALF = "half"
    CLOSED = "closed"


class AdjustmentType(StrEnum):
    FORWARD = "forward"
    BACKWARD = "backward"

