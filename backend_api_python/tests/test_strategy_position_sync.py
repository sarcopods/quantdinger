"""Tests for local position snapshot helpers used by live sync and UI."""

from app.services.live_trading.records import (
    lookup_exchange_side_qty,
    normalize_strategy_symbol,
    strategy_allowed_symbols,
)


def test_strategy_allowed_symbols_includes_trading_config_symbol():
    sc = {
        "symbol": "",
        "trading_config": {"symbol": "SOL/USDT", "symbol_list": []},
    }
    assert strategy_allowed_symbols(sc) == {"SOL/USDT"}


def test_strategy_allowed_symbols_includes_row_and_list():
    sc = {
        "symbol": "BTC/USDT",
        "trading_config": {
            "symbol": "ETH/USDT",
            "symbol_list": ["Crypto:SOL/USDT", "BNBUSDT"],
        },
    }
    allowed = strategy_allowed_symbols(sc)
    assert "BTC/USDT" in allowed
    assert "ETH/USDT" in allowed
    assert "SOL/USDT" in allowed
    assert normalize_strategy_symbol("BNBUSDT").upper() in allowed


def test_lookup_exchange_side_qty_symbol_aliases():
    exch = {"SOL/USDT": {"long": 1.5, "short": 0.0}}
    assert lookup_exchange_side_qty(exch, "SOLUSDT", "long") == 1.5
    assert lookup_exchange_side_qty(exch, "SOL/USDT", "short") == 0.0


def test_filter_strategy_positions_by_allowed_symbols():
    """Regression: positions API must not surface unrelated wallet legs."""
    sc = {"symbol": "", "trading_config": {"symbol": "ETH/USDT"}}
    allowed = strategy_allowed_symbols(sc)
    allowed_upper = {
        normalize_strategy_symbol(str(s or "")).upper()
        for s in allowed
        if normalize_strategy_symbol(str(s or ""))
    }
    rows = [
        {"symbol": "ETH/USDT", "side": "short", "size": 0.41},
        {"symbol": "USDT", "side": "long", "size": 362.0},
        {"symbol": "OKB/USDT", "side": "long", "size": 0.6},
    ]
    filtered = [
        r
        for r in rows
        if normalize_strategy_symbol(str(r.get("symbol") or "")).upper() in allowed_upper
    ]
    assert len(filtered) == 1
    assert filtered[0]["symbol"] == "ETH/USDT"


def test_strategy_has_trades_for_symbol_candidates():
    from app.services.live_trading.records import _position_symbol_candidates

    cands = _position_symbol_candidates("ETHUSDT")
    assert "ETH/USDT" in cands
    assert "ETHUSDT" in cands
