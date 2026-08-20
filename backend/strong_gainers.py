"""Independent +40% gainers scanner with resilient batch discovery."""
from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
import yfinance as yf
from backend.gainers_universe import get_universe

DEFAULT_UNIVERSE = get_universe()


def _num(value: Any, default: float = 0.0) -> float:
    try: return float(value)
    except (TypeError, ValueError): return default


def _score_momentum(change: float, rsi: float, price_vs_high: float) -> float:
    score = min(100.0, max(0.0, change * 1.5))
    if 55 <= rsi <= 80: score += 15
    elif rsi > 90: score -= 8
    if price_vs_high >= 0: score += 10
    return round(min(100.0, max(0.0, score)), 1)


def _score_liquidity(volume: float, avg_volume: float, dollar_volume: float) -> tuple[float, float]:
    rvol = volume / avg_volume if avg_volume > 0 else 0.0
    score = min(100.0, rvol * 25)
    if dollar_volume >= 50_000_000: score += 25
    elif dollar_volume >= 10_000_000: score += 15
    elif dollar_volume >= 2_000_000: score += 8
    return round(min(100.0, score), 1), round(rvol, 2)


def _extract(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(data.columns, pd.MultiIndex):
        try: return data[symbol].dropna(how="all")
        except Exception: return pd.DataFrame()
    return data.dropna(how="all")


def analyze_gainers(symbols: list[str], period: str = "5d") -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    clean = list(dict.fromkeys(str(s).strip().upper() for s in symbols if str(s).strip()))
    if not clean: return pd.DataFrame()
    try:
        data = yf.download(clean, period=period, interval="1d", group_by="ticker", auto_adjust=False, threads=False, progress=False)
    except Exception: return pd.DataFrame()
    for symbol in clean:
        try:
            frame = _extract(data, symbol)
            if frame.empty or "Close" not in frame or len(frame) < 2: continue
            close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
            volume = pd.to_numeric(frame.get("Volume", 0), errors="coerce").fillna(0)
            if len(close) < 2: continue
            price, previous = _num(close.iloc[-1]), _num(close.iloc[-2])
            change = ((price / previous) - 1) * 100 if previous > 0 else 0
            if change < 40: continue
            vol = _num(volume.iloc[-1]); avg_vol = _num(volume.iloc[:-1].tail(20).mean())
            dollar_volume = price * vol; high = _num(close.tail(252).max(), price)
            price_vs_high = ((price / high) - 1) * 100 if high > 0 else 0
            returns = close.pct_change().dropna(); rsi = 50.0
            if len(returns) >= 14:
                gains = returns.clip(lower=0).rolling(14).mean().iloc[-1]
                losses = (-returns.clip(upper=0)).rolling(14).mean().iloc[-1]
                rsi = 100 - (100 / (1 + gains / losses)) if losses > 0 else 100.0
            momentum = _score_momentum(change, rsi, price_vs_high)
            liquidity, rvol = _score_liquidity(vol, avg_vol, dollar_volume)
            composite = round(momentum * 0.55 + liquidity * 0.45, 1)
            strength = "🔥 انفجار قوي" if composite >= 80 else ("🚀 صعود قوي" if composite >= 65 else ("⚡ ارتفاع مع سيولة" if liquidity >= 65 else "⚠️ ارتفاع ضعيف"))
            rows.append({"symbol":symbol,"price":round(price,2),"change_pct":round(change,2),"momentum_score":momentum,"liquidity_score":liquidity,"volume":int(vol),"relative_volume":rvol,"dollar_volume":round(dollar_volume,0),"rsi":round(rsi,1),"strength":strength,"gainer_score":composite})
        except Exception: continue
    return pd.DataFrame(rows).sort_values(["gainer_score","change_pct"],ascending=False).reset_index(drop=True) if rows else pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def discover_strong_gainers(limit: int = 1500, period: str = "5d") -> pd.DataFrame:
    """Discover +40% names from the independent universe in bounded batches."""
    symbols = list(get_universe())
    if limit > 0: symbols = symbols[:limit]
    results: list[pd.DataFrame] = []
    batch_size = 150
    for start in range(0, len(symbols), batch_size):
        frame = analyze_gainers(symbols[start:start + batch_size], period=period)
        if not frame.empty: results.append(frame)
    if not results: return pd.DataFrame()
    return pd.concat(results, ignore_index=True).drop_duplicates("symbol").sort_values(["gainer_score","change_pct"], ascending=False).reset_index(drop=True)
