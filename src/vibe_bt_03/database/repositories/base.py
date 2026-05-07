from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from vibe_bt_03.database.errors import DatabaseValidationError


class BaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


def validate_price_bar(open_: Decimal, high: Decimal, low: Decimal, close: Decimal) -> None:
    if high < low:
        raise DatabaseValidationError(f"invalid price bar: high {high} is lower than low {low}")
    if open_ < 0 or high < 0 or low < 0 or close < 0:
        raise DatabaseValidationError("price fields must be non-negative")

