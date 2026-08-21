"""Broad US-stock discovery for the Strong Gainers scanner.

The scanner must discover the real leaders first, including small caps and
low-priced stocks. It therefore avoids Yahoo's predefined ``day_gainers`` list,
which applies large-cap / $5+ filters, and instead runs a custom equity query.
Nasdaq/NYSE/AMEX public screener data is merged as a second independent source.
"""
from __future__ import annotations
from typing import Iterable
import re
import pandas as pd
import streamlit as st
import requests

FALLBACK_UNIVERSE = tuple(sorted(set(
    "AAPL MSFT NVDA AMZN META TSLA GOOGL GOOG AVGO AMD NFLX PLTR MU INTC SMCI ARM MRVL QCOM MSTR COIN HOOD MARA CLSK RIOT HUT IREN ASTS RKLB LUNR SOUN RGTI IONQ SMR OKLO SOFI RIVN LCID NIO XPEV LI GME AMC CVNA UPST AFRM APP CRWD SNOW NET DDOG SHOP UBER ABNB DKNG CELH CAVA HIMS TEM AI".split()
)))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AI-Breakout-Scanner/2.0)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nasdaq.com/",
}


def _clean(symbols: Iterable[str]) -> tuple[str, ...]:
    out = []
    for symbol in symbols:
        s = str(symbol).strip().upper().replace(".", "-")
        if s and s.isascii() and len(s) <= 8 and s.replace("-", "").isalnum():
            out.append(s)
    return tuple(sorted(set(out)))


def _number(value, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
    text = re.sub(r"[^0-9+\-.]", "", text)
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _fetch_exchange_rows(exchange: str) -> list[dict]:
    url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000&exchange={exchange}"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    payload = response.json()
    return ((payload.get("data") or {}).get("rows") or [])


def _yahoo_custom_gainers(min_price: float, max_price: float, threshold: float) -> pd.DataFrame:
    """Return broad US gainers from Yahoo without the predefined large-cap filter."""
    try:
        import yfinance as yf
        from yfinance import EquityQuery

        query = EquityQuery("and", [
            EquityQuery("eq", ["region", "us"]),
            EquityQuery("gt", ["percentchange", float(threshold)]),
            EquityQuery("gte", ["intradayprice", float(min_price)]),
            EquityQuery("lte", ["intradayprice", float(max_price)]),
            EquityQuery("gt", ["dayvolume", 1000]),
        ])
        payload = yf.screen(
            query,
            size=250,
            sortField="percentchange",
            sortAsc=False,
        )
        quotes = (payload or {}).get("quotes") or []
    except Exception:
        return pd.DataFrame(columns=["symbol", "market_price", "market_change_pct", "market_volume", "exchange", "source"])

    rows: list[dict] = []
    for q in quotes:
        symbol = str(q.get("symbol") or "").strip().upper().replace(".", "-")
        price = _number(q.get("regularMarketPrice") or q.get("intradayprice"))
        pct = _number(q.get("regularMarketChangePercent") or q.get("percentchange"))
        volume = int(max(0, _number(q.get("regularMarketVolume") or q.get("dayvolume"), 0)))
        if not symbol or not (min_price <= price <= max_price) or pct < threshold:
            continue
        rows.append({
            "symbol": symbol,
            "market_price": round(price, 4),
            "market_change_pct": round(pct, 2),
            "market_volume": volume,
            "exchange": str(q.get("fullExchangeName") or q.get("exchange") or "YAHOO"),
            "source": "Yahoo Custom Screener",
        })
    return pd.DataFrame(rows)


def _nasdaq_gainers(min_price: float, max_price: float, threshold: float) -> pd.DataFrame:
    rows_out: list[dict] = []
    for exchange in ("nasdaq", "nyse", "amex"):
        try:
            rows = _fetch_exchange_rows(exchange)
        except Exception:
            continue
        for row in rows:
            symbol = str(row.get("symbol") or row.get("ticker") or "").strip().upper().replace(".", "-")
            if not symbol:
                continue
            price = _number(row.get("lastsale") or row.get("lastSale") or row.get("last"))
            pct = _number(row.get("pctchange") or row.get("pctChange") or row.get("percentchange") or row.get("percentageChange"))
            volume = int(max(0, _number(row.get("volume"), 0)))
            if not (min_price <= price <= max_price) or pct < threshold:
                continue
            rows_out.append({
                "symbol": symbol,
                "market_price": round(price, 4),
                "market_change_pct": round(pct, 2),
                "market_volume": volume,
                "exchange": exchange.upper(),
                "source": "Nasdaq Public Screener",
            })
    return pd.DataFrame(rows_out)


@st.cache_data(ttl=180, show_spinner=False)
def discover_market_gainers(min_price: float = 0.40, max_price: float = 50.0, threshold: float = 40.0) -> pd.DataFrame:
    """Discover current US market leaders from multiple sources.

    Yahoo custom screener is intentionally broad enough for micro/small-cap
    movers. Nasdaq/NYSE/AMEX is merged to reduce missing-symbol risk. When a
    symbol is present in both, the row with the larger reported percentage move
    wins. Cache is only 3 minutes because this is a live-leaders page.
    """
    frames = [
        _yahoo_custom_gainers(min_price, max_price, threshold),
        _nasdaq_gainers(min_price, max_price, threshold),
    ]
    frames = [f for f in frames if isinstance(f, pd.DataFrame) and not f.empty]
    columns = ["symbol", "market_price", "market_change_pct", "market_volume", "exchange", "source"]
    if not frames:
        return pd.DataFrame(columns=columns)

    combined = pd.concat(frames, ignore_index=True)
    combined["market_change_pct"] = pd.to_numeric(combined["market_change_pct"], errors="coerce").fillna(0)
    combined["market_volume"] = pd.to_numeric(combined["market_volume"], errors="coerce").fillna(0)
    combined = combined.sort_values(["market_change_pct", "market_volume"], ascending=False)
    combined = combined.drop_duplicates("symbol", keep="first")
    return combined[columns].reset_index(drop=True)


@st.cache_data(ttl=21600, show_spinner=False)
def load_us_universe() -> tuple[str, ...]:
    symbols: set[str] = set()
    for exchange in ("nasdaq", "nyse", "amex"):
        try:
            for row in _fetch_exchange_rows(exchange):
                symbol = row.get("symbol") or row.get("ticker")
                if symbol:
                    symbols.add(str(symbol))
        except Exception:
            continue
    if not symbols:
        for url in ("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", "https://en.wikipedia.org/wiki/Nasdaq-100"):
            try:
                tables = pd.read_html(url)
                for table in tables:
                    for col in ("Symbol", "Ticker"):
                        if col in table.columns:
                            symbols.update(table[col].tolist()); break
            except Exception:
                continue
    if not symbols:
        symbols.update(FALLBACK_UNIVERSE)
    return _clean(symbols)


def get_universe(limit: int | None = None) -> tuple[str, ...]:
    symbols = load_us_universe()
    return symbols[:limit] if limit and limit > 0 else symbols


def universe_status() -> dict[str, object]:
    symbols = load_us_universe()
    return {"count": len(symbols), "source": "Yahoo custom top-gainers + Nasdaq/NYSE/AMEX", "cached_hours": 6}
