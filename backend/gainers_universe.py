"""Independent US-stock universe for the +40% scanner.

This module is isolated from the normal opportunity scanner and historical
watchlists. It uses the public Nasdaq screener to discover listed symbols,
then falls back to index constituents when the screener is unavailable.
"""
from __future__ import annotations
from typing import Iterable
import pandas as pd
import streamlit as st
import requests

FALLBACK_UNIVERSE = tuple(sorted(set(
    "AAPL MSFT NVDA AMZN META TSLA GOOGL GOOG AVGO AMD NFLX PLTR MU INTC SMCI ARM MRVL QCOM MSTR COIN HOOD MARA CLSK RIOT HUT IREN ASTS RKLB LUNR SOUN RGTI IONQ SMR OKLO SOFI RIVN LCID NIO XPEV LI GME AMC CVNA UPST AFRM APP CRWD SNOW NET DDOG SHOP UBER ABNB DKNG CELH CAVA HIMS TEM AI".split()
)))


def _clean(symbols: Iterable[str]) -> tuple[str, ...]:
    out = []
    for symbol in symbols:
        s = str(symbol).strip().upper().replace(".", "-")
        if s and s.isascii() and len(s) <= 8 and s.replace("-", "").isalnum():
            out.append(s)
    return tuple(sorted(set(out)))


@st.cache_data(ttl=21600, show_spinner=False)
def load_us_universe() -> tuple[str, ...]:
    """Discover a broad US-listed universe once every 6 hours."""
    symbols: set[str] = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AI-Breakout-Scanner/1.0)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nasdaq.com/",
    }
    for exchange in ("nasdaq", "nyse", "amex"):
        try:
            url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000&exchange={exchange}"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            payload = response.json()
            rows = ((payload.get("data") or {}).get("rows") or [])
            for row in rows:
                symbol = row.get("symbol") or row.get("ticker")
                if symbol:
                    symbols.add(str(symbol))
        except Exception:
            continue

    if not symbols:
        # Public index constituents are a reliable fallback and are cached.
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
