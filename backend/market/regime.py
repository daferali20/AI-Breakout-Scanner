"""Market-regime detection used to contextualize breakout signals."""

from __future__ import annotations

import numpy as np
import pandas as pd


def detect_market_regime(df: pd.DataFrame) -> dict[str, float | str]:
    if df is None or df.empty or "Close" not in df:
        return {"regime": "Unknown", "trend_score": 0.0, "volatility_score": 0.0, "risk_multiplier": 1.0}
    close = pd.to_numeric(df["Close"], errors="coerce").dropna()
    if len(close) < 50:
        return {"regime": "Insufficient Data", "trend_score": 0.0, "volatility_score": 0.0, "risk_multiplier": 1.0}
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    ret = close.pct_change().dropna()
    vol = float(ret.tail(20).std() * np.sqrt(252) * 100)
    trend = float(np.clip((sma20 / sma50 - 1) * 1000 + 50, 0, 100))
    if trend >= 65 and vol < 45:
        regime, multiplier = "Bull", 1.0
    elif trend <= 35:
        regime, multiplier = "Bear", 0.65
    elif vol >= 60:
        regime, multiplier = "High Volatility", 0.75
    else:
        regime, multiplier = "Sideways", 0.85
    return {"regime": regime, "trend_score": round(trend, 2), "volatility_score": round(min(vol, 100), 2), "risk_multiplier": multiplier}
