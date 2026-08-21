"""Independent +40% gainers scanner with price filtering and Yahoo throttling."""
from __future__ import annotations
from typing import Any
import time
import random
import pandas as pd
import streamlit as st
import yfinance as yf
from backend.gainers_universe import get_universe

MIN_PRICE = 0.40
MAX_PRICE = 50.00
BATCH_SIZE = 100
BATCH_DELAY_SECONDS = 3.0
RETRY_DELAYS = (8.0, 20.0, 45.0)


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


def _download_batch(symbols: list[str], period: str) -> pd.DataFrame:
    """Download one controlled batch and retry rate-limit failures."""
    for attempt, delay in enumerate((0.0, *RETRY_DELAYS)):
        if delay:
            time.sleep(delay + random.uniform(0.0, 1.5))
        try:
            return yf.download(
                symbols,
                period=period,
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                threads=False,
                progress=False,
            )
        except Exception as exc:
            if "RateLimit" not in type(exc).__name__ and "Too Many Requests" not in str(exc):
                return pd.DataFrame()
            if attempt == len(RETRY_DELAYS):
                return pd.DataFrame()
    return pd.DataFrame()


def analyze_gainers(symbols: list[str], threshold: float = 40.0, period: str = "3mo", min_price: float = MIN_PRICE, max_price: float = MAX_PRICE) -> tuple[pd.DataFrame, dict[str, int]]:
    """Find >= threshold gainers whose latest price is between min_price and max_price."""
    rows: list[dict[str, Any]] = []
    stats = {"requested": 0, "with_data": 0, "price_range": 0, "above_threshold": 0}
    clean = list(dict.fromkeys(str(s).strip().upper() for s in symbols if str(s).strip()))
    stats["requested"] = len(clean)
    if not clean: return pd.DataFrame(), stats

    for batch_start in range(0, len(clean), BATCH_SIZE):
        batch = clean[batch_start:batch_start + BATCH_SIZE]
        data = _download_batch(batch, period)
        if data.empty:
            continue
        for symbol in batch:
            try:
                frame = _extract(data, symbol)
                if frame.empty or "Close" not in frame or len(frame) < 2: continue
                close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
                volume = pd.to_numeric(frame.get("Volume", 0), errors="coerce").fillna(0)
                if len(close) < 2: continue
                stats["with_data"] += 1
                price = _num(close.iloc[-1])
                if not (min_price <= price <= max_price): continue
                stats["price_range"] += 1
                candidates = []
                for label, days in (("اليوم", 1), ("3 أيام", 3), ("5 أيام", 5), ("20 يوم", 20), ("60 يوم", 60)):
                    if len(close) > days:
                        base = _num(close.iloc[-days-1])
                        if base > 0: candidates.append((label, ((price / base) - 1) * 100, days))
                if not candidates: continue
                period_label, change, change_days = max(candidates, key=lambda x: x[1])
                if change < threshold: continue
                stats["above_threshold"] += 1
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
                rows.append({"symbol":symbol,"price":round(price,2),"change_pct":round(change,2),"period":period_label,"period_days":change_days,"momentum_score":momentum,"liquidity_score":liquidity,"volume":int(vol),"relative_volume":rvol,"dollar_volume":round(dollar_volume,0),"rsi":round(rsi,1),"strength":strength,"gainer_score":composite})
            except Exception:
                continue
        if batch_start + BATCH_SIZE < len(clean):
            time.sleep(BATCH_DELAY_SECONDS + random.uniform(0.0, 1.0))
    result = pd.DataFrame(rows)
    if result.empty: return result, stats
    return result.sort_values(["gainer_score","change_pct"], ascending=False).reset_index(drop=True), stats


@st.cache_data(ttl=1800, show_spinner=False)
def discover_strong_gainers(limit: int = 1500, threshold: float = 40.0, period: str = "3mo", min_price: float = MIN_PRICE, max_price: float = MAX_PRICE) -> tuple[pd.DataFrame, dict[str, int]]:
    symbols = list(get_universe())
    if limit > 0: symbols = symbols[:limit]
    return analyze_gainers(symbols, threshold=threshold, period=period, min_price=min_price, max_price=max_price)
