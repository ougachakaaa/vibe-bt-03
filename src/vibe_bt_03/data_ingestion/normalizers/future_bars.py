from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from vibe_bt_03.data_ingestion.normalizers.common import (first_value,
                                                          normalize_provider,
                                                          parse_bool,
                                                          parse_date,
                                                          parse_decimal)
from vibe_bt_03.database.api.types import FutureDailyBarInput


def normalize_future_daily_bars(
    provider: str,
    records: Sequence[Mapping[str, Any]],
) -> list[FutureDailyBarInput]:
    normalize_provider(provider)
    return [
        FutureDailyBarInput(
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
            settlement=parse_decimal(first_value(record, "settle", "settlement", "结算价"), field_name="settlement", required=False),
            pre_settlement=parse_decimal(
                first_value(record, "pre_settle", "pre_settlement", "昨结"),
                field_name="pre_settlement",
                required=False,
            ),
            open_interest=parse_decimal(first_value(record, "oi", "open_interest", "持仓量"), field_name="open_interest", required=False),
            pre_open_interest=parse_decimal(
                first_value(record, "pre_oi", "pre_open_interest", "昨持仓"),
                field_name="pre_open_interest",
                required=False,
            ),
            change_open_interest=parse_decimal(
                first_value(record, "change_oi", "change_open_interest", "增仓"),
                field_name="change_open_interest",
                required=False,
            ),
            upper_limit=parse_decimal(first_value(record, "upper_limit", "涨停价"), field_name="upper_limit", required=False),
            lower_limit=parse_decimal(first_value(record, "lower_limit", "跌停价"), field_name="lower_limit", required=False),
            is_main_contract=parse_bool(first_value(record, "is_main_contract", "主力合约"), default=False),
        )
        for record in records
    ]
