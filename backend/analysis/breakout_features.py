"""Unified, explainable breakout feature extraction."""

from __future__ import annotations

import numpy as np
import pandas as pd


def extract_breakout_features(df: pd.DataFrame) -> dict[str, float]:
    if df is None or df.empty:
        return {}
    x = df.copy()
    close = pd.to_numeric(x["Close"], errors="coerce")
    high = pd.to_numeric(x["High"], errors="coerce")
    low = pd.to_numeric(x["Low"], errors="coerce")
    volume = pd.to_numeric(x["Volume"], errors="coerce").fillna(0)
    price = float(close.iloc[-1])
    avg_volume = float(volume.iloc[-21:-1].mean()) if len(x) > 21 else float(volume.mean())
    rvol = float(volume.iloc[-1] / avg_volume) if avg_volume > 0 else 1.0
    resistance = float(high.iloc[-21:-1].max()) if len(x) > 21 else float(high.max())
    support = float(low.iloc[-21:-1].min()) if len(x) > 21 else float(low.min())
    atr = float((high - low).rolling(14).mean().iloc[-1]) if len(x) >= 14 else float((high - low).mean())
    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(x) >= 20 else price
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(x) >= 50 else sma20
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean().replace(0, np.nan)
    rsi = float((100 - 100 / (1 + gain / loss)).iloc[-1]) if len(x) >= 14 else 50.0
    rsi = 50.0 if not np.isfinite(rsi) else rsi
    price_position = (price - support) / (resistance - support) if resistance > support else 0.5
    distance = (resistance - price) / price if price else 0.0
    resistance_break = price / resistance if resistance else 1.0
    momentum_5d = float(close.pct_change(5).iloc[-1] * 100) if len(x) > 5 else 0.0
    momentum_20d = float(close.pct_change(20).iloc[-1] * 100) if len(x) > 20 else momentum_5d
    atr_ratio = atr / price if price else 0.0
    volume_trend = float(volume.tail(5).mean() / volume.tail(20).mean()) if volume.tail(20).mean() > 0 else 1.0
    trend_strength = float(np.clip((sma20 / sma50 - 1) * 10 + 0.5, 0, 1)) if sma50 else 0.5
    smart_money = float(np.clip(50 + momentum_5d * 2 + (rvol - 1) * 10, 0, 100))
    compression = float(np.clip(1 - atr_ratio / 0.05, 0, 1))
    return {
        "rsi": rsi,
        "relative_volume": rvol,
        "volume_trend": volume_trend,
        "smart_money_score": smart_money,
        "trend_strength": trend_strength,
        "price_position": float(np.clip(price_position, 0, 1)),
        "resistance_distance": distance,
        "resistance_break": resistance_break,
        "bollinger_width": float(close.rolling(20).std().iloc[-1] * 4 / price) if len(x) >= 20 and price else 0.0,
        "atr_ratio": atr_ratio,
        "price_change": float(close.pct_change().iloc[-1] * 100) if len(x) > 1 else 0.0,
        "price_momentum": momentum_20d,
        "compression_level": compression,
    }
