"""Live US market leaders discovery.

Discovery intentionally does NOT use Yahoo. Primary source is TradingView's
America scanner; Nasdaq public screener is a fallback. Historical enrichment
can be performed later by the existing strong-gainers analyzer.
"""
from __future__ import annotations

from typing import Any
import re
import pandas as pd
import requests
import streamlit as st

TV_URL = "https://scanner.tradingview.com/america/scan"
NASDAQ_URL = "https://api.nasdaq.com/api/screener/stocks"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
    text = re.sub(r"[^0-9+\-.]", "", text)
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _normalize_symbol(raw: str) -> str:
    symbol = str(raw or "").strip().upper()
    if ":" in symbol:
        symbol = symbol.split(":", 1)[1]
    return symbol.replace(".", "-")


def _tradingview_scan(min_price: float, max_price: float, min_change: float, limit: int) -> pd.DataFrame:
    columns = [
        "name",
        "description",
        "close",
        "change",
        "volume",
        "relative_volume_10d_calc",
        "market_cap_basic",
        "exchange",
        "type",
        "subtype",
    ]
    payload = {
        "filter": [
            {"left": "close", "operation": "egreater", "right": min_price},
            {"left": "close", "operation": "eless", "right": max_price},
            {"left": "change", "operation": "egreater", "right": min_change},
        ],
        "options": {"lang": "en"},
        "markets": ["america"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": columns,
        "sort": {"sortBy": "change", "sortOrder": "desc"},
        "range": [0, max(50, min(int(limit), 1000))],
    }
    response = requests.post(TV_URL, headers=HEADERS, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json().get("data") or []
    rows: list[dict[str, Any]] = []
    for item in data:
        values = item.get("d") or []
        if len(values) < len(columns):
            values = list(values) + [None] * (len(columns) - len(values))
        row = dict(zip(columns, values))
        symbol = _normalize_symbol(row.get("name") or item.get("s"))
        exchange = str(row.get("exchange") or "").upper()
        instrument_type = str(row.get("type") or "").lower()
        subtype = str(row.get("subtype") or "").lower()
        price = _num(row.get("close"))
        change = _num(row.get("change"))
        volume = int(max(0, _num(row.get("volume"))))
        rvol = _num(row.get("relative_volume_10d_calc"))
        market_cap = _num(row.get("market_cap_basic"))
        if exchange not in {"NASDAQ", "NYSE", "AMEX", "NYSEARCA", "NYSEAMERICAN"}:
            continue
        if instrument_type and instrument_type != "stock":
            continue
        # Exclude obvious funds/ETFs when TradingView labels subtype.
        if subtype in {"etf", "fund", "dr", "preferred"}:
            continue
        if not symbol or not (min_price <= price <= max_price) or change < min_change:
            continue
        rows.append({
            "symbol": symbol,
            "company": str(row.get("description") or ""),
            "price": round(price, 4),
            "change_pct": round(change, 2),
            "volume": volume,
            "relative_volume": round(rvol, 2),
            "dollar_volume": round(price * volume, 0),
            "market_cap": round(market_cap, 0),
            "exchange": exchange,
            "source": "TradingView Market Scanner",
        })
    return pd.DataFrame(rows)


def _nasdaq_scan(min_price: float, max_price: float, min_change: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    headers = {**HEADERS, "Referer": "https://www.nasdaq.com/market-activity/stocks/screener"}
    for exchange in ("nasdaq", "nyse", "amex"):
        try:
            response = requests.get(
                NASDAQ_URL,
                headers=headers,
                params={"tableonly": "true", "limit": 5000, "exchange": exchange},
                timeout=18,
            )
            response.raise_for_status()
            items = ((response.json().get("data") or {}).get("rows") or [])
        except Exception:
            continue
        for item in items:
            symbol = _normalize_symbol(item.get("symbol"))
            price = _num(item.get("lastsale") or item.get("lastSale"))
            change = _num(item.get("pctchange") or item.get("pctChange"))
            volume = int(max(0, _num(item.get("volume"))))
            if symbol and min_price <= price <= max_price and change >= min_change:
                rows.append({
                    "symbol": symbol,
                    "company": str(item.get("name") or ""),
                    "price": round(price, 4),
                    "change_pct": round(change, 2),
                    "volume": volume,
                    "relative_volume": 0.0,
                    "dollar_volume": round(price * volume, 0),
                    "market_cap": _num(item.get("marketCap")),
                    "exchange": exchange.upper(),
                    "source": "Nasdaq Public Screener",
                })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60, show_spinner=False)
def discover_live_leaders(
    min_price: float = 0.40,
    max_price: float = 50.0,
    min_change: float = 40.0,
    limit: int = 300,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return current US leaders sorted strictly by percentage change."""
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    try:
        tv = _tradingview_scan(min_price, max_price, min_change, limit)
        if not tv.empty:
            frames.append(tv)
    except Exception as exc:
        errors.append(f"TradingView: {exc}")

    # Always add Nasdaq as a second independent discovery source; duplicates
    # are later collapsed in favor of TradingView because it is appended first.
    try:
        nasdaq = _nasdaq_scan(min_price, max_price, min_change)
        if not nasdaq.empty:
            frames.append(nasdaq)
    except Exception as exc:
        errors.append(f"Nasdaq: {exc}")

    if not frames:
        return pd.DataFrame(), {"sources": [], "errors": errors, "count": 0}

    combined = pd.concat(frames, ignore_index=True)
    combined["change_pct"] = pd.to_numeric(combined["change_pct"], errors="coerce").fillna(0)
    combined["price"] = pd.to_numeric(combined["price"], errors="coerce").fillna(0)
    combined["volume"] = pd.to_numeric(combined["volume"], errors="coerce").fillna(0)
    combined["dollar_volume"] = pd.to_numeric(combined["dollar_volume"], errors="coerce").fillna(0)
    combined = combined[
        combined["price"].between(min_price, max_price)
        & (combined["change_pct"] >= min_change)
    ]
    combined = (
        combined.sort_values(["change_pct", "volume"], ascending=False)
        .drop_duplicates("symbol", keep="first")
        .head(limit)
        .reset_index(drop=True)
    )
    sources = sorted(set(combined["source"].astype(str))) if not combined.empty else []
    return combined, {"sources": sources, "errors": errors, "count": len(combined)}
