from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from vibe_bt_03.data_ingestion.normalizers.common import (first_value,
                                                          normalize_provider,
                                                          parse_bool,
                                                          parse_date,
                                                          parse_decimal)
from vibe_bt_03.database.api.types import StockDailyBarInput


def normalize_stock_daily_bars(
    provider: str,
    records: Sequence[Mapping[str, Any]],
) -> list[StockDailyBarInput]:
    normalize_provider(provider)
    return [
        StockDailyBarInput(
            trade_date=parse_date(
                first_value(record, "trade_date", "date", "日期"),
                field_name="trade_date",
            ),
            open=parse_decimal(first_value(record, "open", "开盘"), field_name="open"),
            high=parse_decimal(first_value(record, "high", "最高"), field_name="high"),
            low=parse_decimal(first_value(record, "low", "最低"), field_name="low"),
            close=parse_decimal(first_value(record, "close", "收盘"), field_name="close"),
            volume=parse_decimal(first_value(record, "vol", "volume", "成交量"), field_name="volume", required=False),
            amount=parse_decimal(first_value(record, "amount", "成交额"), field_name="amount", required=False),
            source=provider,
            pre_close=parse_decimal(first_value(record, "pre_close", "昨收"), field_name="pre_close", required=False),
            turnover_rate=parse_decimal(
                first_value(record, "turnover_rate", "换手率"),
                field_name="turnover_rate",
                required=False,
            ),
            limit_up=parse_decimal(first_value(record, "limit_up", "涨停价"), field_name="limit_up", required=False),
            limit_down=parse_decimal(first_value(record, "limit_down", "跌停价"), field_name="limit_down", required=False),
            is_suspended=parse_bool(first_value(record, "is_suspended", "停牌"), default=False),
        )
        for record in records
    ]
