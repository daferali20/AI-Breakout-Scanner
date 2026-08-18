"""Technical feature engine for AI Breakout Scanner."""

from typing import Dict

import numpy as np
import pandas as pd


def _true_range(df: pd.DataFrame) -> pd.Series:
    prev = df["Close"].shift(1)
    return pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()],
        axis=1,
    ).max(axis=1)


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Bollinger/Keltner squeeze and core trend features."""
    df = df.copy()
    if df.empty:
        return df
    close, high, low, volume = df["Close"], df["High"], df["Low"], df["Volume"]
    df["SMA20"] = close.rolling(20).mean()
    df["SMA50"] = close.rolling(50).mean()
    df["SMA200"] = close.rolling(200).mean()
    df["STD20"] = close.rolling(20).std()
    df["BB_Upper"] = df["SMA20"] + 2 * df["STD20"]
    df["BB_Lower"] = df["SMA20"] - 2 * df["STD20"]
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["SMA20"]
    df["TR"] = _true_range(df)
    df["ATR14"] = df["TR"].ewm(alpha=1 / 14, adjust=False).mean()
    df["ATR20"] = df["TR"].rolling(20).mean()
    df["ATR_Ratio"] = df["ATR14"] / close
    df["KC_Upper"] = df["SMA20"] + 1.5 * df["ATR20"]
    df["KC_Lower"] = df["SMA20"] - 1.5 * df["ATR20"]
    df["Squeeze_On"] = (df["BB_Upper"] < df["KC_Upper"]) & (df["BB_Lower"] > df["KC_Lower"])
    df["RVOL"] = volume / volume.rolling(20).mean().shift(1)
    df["Momentum_5D"] = close.pct_change(5)
    df["Momentum_20D"] = close.pct_change(20)
    df["High_20"] = high.rolling(20).max().shift(1)
    df["Low_20"] = low.rolling(20).min().shift(1)
    df["Resistance_Distance"] = (df["High_20"] - close) / close
    df["Resistance_Break"] = close / df["High_20"]
    return df


class TechnicalIndicators:
    """Calculate normalized features and scores used by the scanner."""

    def calculate_all(self, df: pd.DataFrame) -> Dict[str, float]:
        if df is None or df.empty or len(df) < 20:
            return self._default_values()
        try:
            clean = df[["Open", "High", "Low", "Close", "Volume"]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            if len(clean) < 20:
                return self._default_values()
            ind = calculate_indicators(clean)
            close = clean["Close"]
            latest = ind.iloc[-1]
            rsi = self._calculate_rsi(close)
            rvol = self._safe(latest.get("RVOL"), 1.0)
            atr_ratio = self._safe(latest.get("ATR_Ratio"), 0.03)
            bb_width = self._safe(latest.get("BB_Width"), 0.10)
            resistance_distance = max(0.0, self._safe(latest.get("Resistance_Distance"), 1.0))
            resistance_break = self._safe(latest.get("Resistance_Break"), 1.0)
            momentum_5 = self._safe(latest.get("Momentum_5D"), 0.0)
            momentum_20 = self._safe(latest.get("Momentum_20D"), 0.0)
            squeeze_on = bool(latest.get("Squeeze_On", False))
            trend = self._trend_strength(ind)
            breakout_confirmed = bool(resistance_break >= 1.0 and rvol >= 1.5 and momentum_5 > 0)
            return {
                "rsi": round(rsi, 2),
                "rsi_score": round(self._rsi_score(rsi), 2),
                "volume_ratio": round(rvol, 2),
                "relative_volume": round(rvol, 2),
                "volume_score": round(self._volume_score(rvol), 2),
                "volatility_score": round(self._volatility_score(atr_ratio), 2),
                "atr_ratio": round(atr_ratio, 5),
                "bollinger_width": round(bb_width, 5),
                "price_position": round(self._price_position(close, clean["High"]), 4),
                "price_trend": round(momentum_20, 5),
                "price_momentum": round(1 + momentum_5, 5),
                "momentum_5d": round(momentum_5, 5),
                "momentum_20d": round(momentum_20, 5),
                "resistance_distance": round(resistance_distance, 5),
                "resistance_break": round(resistance_break, 5),
                "volume_spike": round(rvol, 2),
                "trend_strength": round(trend, 4),
                "squeeze_on": squeeze_on,
                "breakout_confirmed": breakout_confirmed,
                "breakout_score": round(self._breakout_score(ind), 2),
            }
        except Exception:
            return self._default_values()

    def _default_values(self) -> Dict[str, float]:
        return {
            "rsi": 50.0, "rsi_score": 50.0, "volume_ratio": 1.0,
            "relative_volume": 1.0, "volume_score": 40.0, "volatility_score": 50.0,
            "atr_ratio": 0.03, "bollinger_width": 0.10, "price_position": 0.5,
            "price_trend": 0.0, "price_momentum": 1.0, "momentum_5d": 0.0,
            "momentum_20d": 0.0, "resistance_distance": 1.0, "resistance_break": 1.0,
            "volume_spike": 1.0, "trend_strength": 0.5, "squeeze_on": False,
            "breakout_confirmed": False, "breakout_score": 50.0,
        }

    @staticmethod
    def _calculate_rsi(close: pd.Series, period: int = 14) -> float:
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - 100 / (1 + rs)
        value = rsi.iloc[-1]
        return float(np.clip(value, 0, 100)) if pd.notna(value) else 50.0

    @staticmethod
    def _rsi_score(rsi: float) -> float:
        if 50 <= rsi <= 68: return 90.0
        if 45 <= rsi <= 72: return 75.0
        if 35 <= rsi <= 80: return 55.0
        return 25.0

    @staticmethod
    def _volume_score(rvol: float) -> float:
        return float(np.clip((rvol - 0.5) * 50, 0, 100))

    @staticmethod
    def _volatility_score(atr_ratio: float) -> float:
        if atr_ratio <= 0: return 50.0
        return float(np.clip(100 - abs(atr_ratio - 0.025) / 0.025 * 55, 0, 100))

    @staticmethod
    def _price_position(close: pd.Series, high: pd.Series) -> float:
        window = min(len(high), 252)
        high_52 = high.iloc[-window:].max()
        return float(np.clip(close.iloc[-1] / high_52, 0, 1)) if high_52 > 0 else 0.5

    @staticmethod
    def _trend_strength(ind: pd.DataFrame) -> float:
        close = ind["Close"]
        if len(close) < 50: return 0.5
        fast, slow = ind["SMA20"].iloc[-1], ind["SMA50"].iloc[-1]
        slope = close.pct_change(20).iloc[-1]
        if not np.isfinite(fast) or not np.isfinite(slow): return 0.5
        return float(np.clip(0.5 + 2.5 * (fast / slow - 1) + 1.5 * slope, 0, 1))

    @classmethod
    def _breakout_score(cls, ind: pd.DataFrame) -> float:
        row = ind.iloc[-1]
        rvol = cls._safe(row.get("RVOL"), 1)
        distance = max(0, cls._safe(row.get("Resistance_Distance"), 1))
        momentum = cls._safe(row.get("Momentum_5D"), 0)
        trend = cls._trend_strength(ind)
        score = np.clip(rvol / 2.5, 0, 1) * 30
        score += np.clip(1 - distance / 0.08, 0, 1) * 25
        score += np.clip((momentum + 0.02) / 0.08, 0, 1) * 20
        score += trend * 15
        score += 10 if bool(row.get("Squeeze_On", False)) else 0
        return float(np.clip(score, 0, 100))

    @staticmethod
    def _safe(value: float, default: float) -> float:
        try:
            value = float(value)
            return default if not np.isfinite(value) else value
        except (TypeError, ValueError):
            return default
