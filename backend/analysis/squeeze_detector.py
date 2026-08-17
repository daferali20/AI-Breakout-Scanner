"""Squeeze detector using Bollinger Bands and Keltner Channels."""

from typing import Dict

import numpy as np
import pandas as pd


class SqueezeDetector:
    """Detect volatility compression from OHLC data."""

    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, kc_period: int = 20, kc_atr_multiplier: float = 1.5):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.kc_period = kc_period
        self.kc_atr_multiplier = kc_atr_multiplier

    def detect(self, df: pd.DataFrame) -> Dict:
        if df is None or df.empty or len(df) < max(self.bb_period, 20):
            return {"error": "بيانات غير كافية"}
        try:
            close = pd.to_numeric(df["Close"], errors="coerce")
            high = pd.to_numeric(df["High"], errors="coerce")
            low = pd.to_numeric(df["Low"], errors="coerce")
            clean = pd.DataFrame({"Close": close, "High": high, "Low": low}).dropna()
            if len(clean) < self.bb_period:
                return {"error": "بيانات غير كافية"}

            close, high, low = clean["Close"], clean["High"], clean["Low"]
            bb_middle = close.rolling(self.bb_period).mean()
            bb_std = close.rolling(self.bb_period).std()
            bb_upper = bb_middle + bb_std * self.bb_std
            bb_lower = bb_middle - bb_std * self.bb_std
            bb_width = (bb_upper - bb_lower) / bb_middle.replace(0, np.nan)

            prev_close = close.shift(1)
            true_range = pd.concat(
                [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
            ).max(axis=1)
            atr = true_range.ewm(alpha=1 / 14, adjust=False).mean()
            kc_middle = close.rolling(self.kc_period).mean()
            kc_upper = kc_middle + atr * self.kc_atr_multiplier
            kc_lower = kc_middle - atr * self.kc_atr_multiplier
            kc_width = (kc_upper - kc_lower) / kc_middle.replace(0, np.nan)

            bb = float(bb_width.iloc[-1])
            kc = float(kc_width.iloc[-1])
            if not np.isfinite(bb) or not np.isfinite(kc) or kc <= 0:
                return {"error": "تعذر حساب الانضغاط"}

            ratio = bb / kc
            squeeze_score = np.clip(100 - ratio * 70, 0, 100)
            return {
                "is_squeeze": bool(bb < kc),
                "squeeze_score": round(float(squeeze_score), 2),
                "bb_width": round(bb, 5),
                "kc_width": round(kc, 5),
                "ratio": round(ratio, 3),
            }
        except Exception as exc:
            return {"error": str(exc)}
