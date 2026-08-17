"""Real liquidity and money-flow analysis for the breakout engine."""

from typing import Any, Dict

import numpy as np
import pandas as pd

from backend.opportunity import PhaseDetector


class LiquidityAnalyzer:
    """Calculate liquidity, compression, volume and money-flow features."""

    def __init__(self) -> None:
        self.phase_detector = PhaseDetector()

    def analyze_liquidity(
        self, price_data: Any, volume_data: Any = None
    ) -> Dict[str, Any]:
        """Analyze a DataFrame or legacy price/volume dictionaries.

        The previous implementation returned hard-coded placeholder values.
        This version derives every metric from the supplied OHLCV data.
        """
        df = self._to_dataframe(price_data, volume_data)
        if df.empty or len(df) < 20:
            return self._defaults()

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        bb_width = ((sma20 + 2 * std20) - (sma20 - 2 * std20)) / sma20

        tr = self._true_range(df)
        atr14 = tr.rolling(14).mean()
        atr_ratio = (atr14 / close).replace([np.inf, -np.inf], np.nan)

        avg_volume = volume.rolling(20).mean()
        volume_ratio = (volume / avg_volume.replace(0, np.nan)).replace(
            [np.inf, -np.inf], np.nan
        )
        volume_trend = self._safe_float(volume_ratio.iloc[-1], 1.0)

        # Money-flow proxy: CLV * volume, normalized against recent volume.
        spread = (high - low).replace(0, np.nan)
        clv = (((close - low) - (high - close)) / spread).clip(-1, 1).fillna(0)
        mfv = clv * volume
        money_flow_20 = mfv.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)
        smart_money_flow = self._safe_float(money_flow_20.iloc[-1], 0.0)
        smart_money_score = float(np.clip((smart_money_flow + 1) * 50, 0, 100))

        trend_strength = self._calculate_trend_strength(close)
        returns = close.pct_change().dropna()
        volatility = self._safe_float(returns.rolling(20).std().iloc[-1], 0.0)

        recent_high = high.rolling(20).max().shift(1)
        current = self._safe_float(close.iloc[-1], 0.0)
        resistance = self._safe_float(recent_high.iloc[-1], current)
        resistance_distance = max(0.0, (resistance - current) / current) if current else 1.0
        volume_spike = volume_trend
        price_change = self._safe_float(close.pct_change(5).iloc[-1], 0.0)

        data = {
            "bollinger_width": self._safe_float(bb_width.iloc[-1], 1.0),
            "atr_ratio": self._safe_float(atr_ratio.iloc[-1], 0.05),
            "volume_trend": volume_trend,
            "relative_volume": volume_trend,
            "volume_spike": volume_spike,
            "smart_money_flow": smart_money_flow,
            "smart_money_score": smart_money_score,
            "volatility": volatility,
            "trend_strength": trend_strength,
            "rsi": self._calculate_rsi(close),
            "price_trend": price_change,
            "price_momentum": 1.0 + price_change,
            "price_position": self._price_position(close, high),
            "resistance_distance": resistance_distance,
            "price_change": price_change,
            "resistance_break": current / resistance if resistance else 1.0,
        }

        phase_metrics = self.phase_detector.get_phase_metrics(data, "")
        compression_level = float(
            np.clip(1.0 - data["bollinger_width"] / 0.30, 0, 1)
        )

        return {
            **data,
            "phase": phase_metrics.phase,
            "phase_days": phase_metrics.days_in_phase,
            "is_compressed": data["bollinger_width"] < 0.30 and data["atr_ratio"] < 0.04,
            "compression_level": compression_level,
        }

    @staticmethod
    def _to_dataframe(price_data: Any, volume_data: Any = None) -> pd.DataFrame:
        if isinstance(price_data, pd.DataFrame):
            df = price_data.copy()
        elif isinstance(price_data, dict):
            # Accept both lowercase legacy dictionaries and OHLCV dictionaries.
            raw = {str(k).capitalize(): v for k, v in price_data.items()}
            if volume_data is not None:
                raw["Volume"] = volume_data
            df = pd.DataFrame(raw)
        else:
            return pd.DataFrame()

        rename = {c: str(c).capitalize() for c in df.columns}
        df = df.rename(columns=rename)
        required = ["High", "Low", "Close", "Volume"]
        if not all(c in df.columns for c in required):
            return pd.DataFrame()
        return df[required].apply(pd.to_numeric, errors="coerce").dropna()

    @staticmethod
    def _true_range(df: pd.DataFrame) -> pd.Series:
        prev_close = df["Close"].shift(1)
        return pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

    @staticmethod
    def _calculate_rsi(close: pd.Series, period: int = 14) -> float:
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return float(np.clip(rsi.iloc[-1], 0, 100)) if pd.notna(rsi.iloc[-1]) else 50.0

    @staticmethod
    def _calculate_trend_strength(close: pd.Series) -> float:
        if len(close) < 50:
            return 0.5
        fast = close.ewm(span=20, adjust=False).mean().iloc[-1]
        slow = close.ewm(span=50, adjust=False).mean().iloc[-1]
        slope = close.pct_change(20).iloc[-1]
        strength = 0.5 + 3.0 * (fast / slow - 1.0) + 2.0 * slope
        return float(np.clip(strength, 0, 1))

    @staticmethod
    def _price_position(close: pd.Series, high: pd.Series) -> float:
        window = min(len(high), 252)
        high_52 = high.iloc[-window:].max()
        return float(np.clip(close.iloc[-1] / high_52, 0, 1)) if high_52 > 0 else 0.5

    @staticmethod
    def _safe_float(value: Any, default: float) -> float:
        try:
            value = float(value)
            return default if not np.isfinite(value) else value
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _defaults() -> Dict[str, Any]:
        return {
            "bollinger_width": 1.0,
            "atr_ratio": 0.05,
            "volume_trend": 1.0,
            "relative_volume": 1.0,
            "volume_spike": 1.0,
            "smart_money_flow": 0.0,
            "smart_money_score": 50.0,
            "volatility": 0.0,
            "trend_strength": 0.5,
            "rsi": 50.0,
            "price_trend": 0.0,
            "price_momentum": 1.0,
            "price_position": 0.5,
            "resistance_distance": 1.0,
            "price_change": 0.0,
            "resistance_break": 1.0,
            "is_compressed": False,
            "compression_level": 0.0,
        }
