from __future__ import annotations

from dataclasses import dataclass

from vibe_bt_03.data_ingestion import resolvers
from vibe_bt_03.data_ingestion.resolvers import InstrumentResolver
from vibe_bt_03.database.api.types import InstrumentView
from vibe_bt_03.database.models.enums import (AssetClass, Exchange,
                                              InstrumentInfoLevel)


def make_view(symbol: str = "000001.SZ") -> InstrumentView:
    return InstrumentView(
        symbol=symbol,
        asset_class=AssetClass.STOCK,
        info_level=InstrumentInfoLevel.BASIC,
        exchange=Exchange.SZSE,
        name="平安银行",
        status=None,
        listed_date=None,
        delisted_date=None,
        price_tick=None,
        multiplier=None,
        extra={},
    )


@dataclass
class FakeProviderSource:
    source_name: str = "tushare"
    fetched: bool = False

    def fetch_stock_instrument_records(self, symbol):
        self.fetched = True
        return [{"ts_code": symbol, "name": "平安银行"}]

    def fetch_future_instrument_records(self, symbol):
        raise NotImplementedError


def test_resolver_returns_existing_instrument_without_fetch(monkeypatch) -> None:
    source = FakeProviderSource()
    monkeypatch.setattr(resolvers, "get_instrument", lambda symbol: make_view(symbol))

    result = InstrumentResolver(source).ensure_stock_instrument("000001.SZ")

    assert result is not None
    assert result.symbol == "000001.SZ"
    assert not source.fetched


def test_resolver_saves_missing_instrument(monkeypatch) -> None:
    source = FakeProviderSource()
    saved_assets = []
    saved_instruments = []
    calls = {"get": 0}

    def fake_get_instrument(symbol):
        calls["get"] += 1
        return None if calls["get"] == 1 else make_view(symbol)

    monkeypatch.setattr(resolvers, "get_instrument", fake_get_instrument)
    monkeypatch.setattr(resolvers, "save_assets", lambda items, overwrite=True: saved_assets.extend(items))
    monkeypatch.setattr(resolvers, "save_instruments", lambda items, overwrite=True: saved_instruments.extend(items))

    result = InstrumentResolver(source).ensure_stock_instrument("000001.SZ")

    assert result is not None
    assert source.fetched
    assert saved_assets[0].code == "000001"
    assert saved_instruments[0].symbol == "000001.SZ"


def test_resolver_dry_run_does_not_write(monkeypatch) -> None:
    source = FakeProviderSource()
    monkeypatch.setattr(resolvers, "get_instrument", lambda symbol: None)
    monkeypatch.setattr(resolvers, "save_assets", lambda items, overwrite=True: (_ for _ in ()).throw(AssertionError))
    monkeypatch.setattr(resolvers, "save_instruments", lambda items, overwrite=True: (_ for _ in ()).throw(AssertionError))

    result = InstrumentResolver(source).ensure_stock_instrument("000001.SZ", dry_run=True)

    assert result is None
    assert source.fetched
