"""Independent US-stock discovery for the +40% scanner.

This module is isolated from the normal opportunity scanner and historical
watchlists. It uses Nasdaq's public screener both for the broad symbol universe
and, when available, for pre-filtering current market gainers before Yahoo is
used for deeper momentum/liquidity analysis.
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
    "User-Agent": "Mozilla/5.0 (compatible; AI-Breakout-Scanner/1.0)",
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


@st.cache_data(ttl=900, show_spinner=False)
def discover_market_gainers(min_price: float = 0.40, max_price: float = 50.0, threshold: float = 40.0) -> pd.DataFrame:
    """Pre-discover current gainers from Nasdaq/NYSE/AMEX screener data.

    This step intentionally avoids Yahoo. Yahoo is only used later for the
    smaller candidate set that survives price/change filtering.
    """
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
            if not (min_price <= price <= max_price):
                continue
            if pct < threshold:
                continue
            rows_out.append({
                "symbol": symbol,
                "market_price": round(price, 4),
                "market_change_pct": round(pct, 2),
                "market_volume": volume,
                "exchange": exchange.upper(),
            })
    if not rows_out:
        return pd.DataFrame(columns=["symbol", "market_price", "market_change_pct", "market_volume", "exchange"])
    return (
        pd.DataFrame(rows_out)
        .drop_duplicates("symbol")
        .sort_values(["market_change_pct", "market_volume"], ascending=False)
        .reset_index(drop=True)
    )


@st.cache_data(ttl=21600, show_spinner=False)
def load_us_universe() -> tuple[str, ...]:
    """Discover a broad US-listed universe once every 6 hours."""
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
        for url in (
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
            "https://en.wikipedia.org/wiki/Nasdaq-100",
        ):
            try:
                tables = pd.read_html(url)
                for table in tables:
                    for col in ("Symbol", "Ticker"):
                        if col in table.columns:
                            symbols.update(table[col].tolist())
                            break
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
    return {
        "count": len(symbols),
        "source": "Nasdaq public screener (Nasdaq/NYSE/AMEX) with index fallback",
        "cached_hours": 6,
    }
