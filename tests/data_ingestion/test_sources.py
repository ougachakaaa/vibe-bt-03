from __future__ import annotations

import pytest

from vibe_bt_03.data_ingestion.sources import AkshareSource, TushareSource


def test_provider_source_names() -> None:
    assert TushareSource().source_name == "tushare"
    assert AkshareSource().source_name == "akshare"


def test_provider_sources_are_explicitly_unimplemented() -> None:
    with pytest.raises(NotImplementedError, match="Tushare stock raw bar"):
        TushareSource().fetch_stock_raw_bar_records("000001.SZ")

    with pytest.raises(NotImplementedError, match="Akshare stock raw bar"):
        AkshareSource().fetch_stock_raw_bar_records("000001.SZ")
