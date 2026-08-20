"""Independent symbol universe for the +40% scanner.

This module is deliberately isolated from the normal opportunity scanner.
It maintains a cached US-stock universe using public index constituent pages
when available, then falls back to a curated liquid universe. It never writes
to opportunity history or the normal scan results.
"""
from __future__ import annotations
from typing import Iterable
import pandas as pd
import streamlit as st
import requests

FALLBACK_UNIVERSE = tuple(sorted(set(
    "AAPL MSFT NVDA AMZN META TSLA GOOGL GOOG AVGO AMD NFLX PLTR MU INTC SMCI ARM MRVL QCOM MSTR COIN HOOD MARA CLSK RIOT HUT IREN ASTS RKLB LUNR SOUN RGTI IONQ SMR OKLO SOFI RIVN LCID NIO XPEV LI GME AMC CVNA UPST AFRM APP CRWD SNOW NET DDOG SHOP UBER ABNB DKNG CELH CAVA HIMS TEM AI TQQQ SQQQ SPY QQQ IWM DIA XLF XLE XLI XLK XLP XLV XLY XLC XLU XLB XBI IBIT FBTC BITB ETHA".split()
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
    """Load a broad US universe once every 6 hours; never called per quote."""
    symbols: set[str] = set()
    urls = (
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "https://en.wikipedia.org/wiki/Nasdaq-100",
    )
    for url in urls:
        try:
            tables = pd.read_html(url)
            for table in tables:
                for col in ("Symbol", "Ticker"):
                    if col in table.columns:
                        symbols.update(_clean(table[col].tolist()))
                        break
        except Exception:
            continue
    if not symbols:
        symbols.update(FALLBACK_UNIVERSE)
    return _clean(symbols)


def get_universe(limit: int | None = None) -> tuple[str, ...]:
    symbols = load_us_universe()
    if limit and limit > 0:
        return symbols[:limit]
    return symbols


def universe_status() -> dict[str, object]:
    symbols = load_us_universe()
    return {
        "count": len(symbols),
        "source": "S&P 500 + Nasdaq-100 public constituents / fallback",
        "cached_hours": 6,
    }
