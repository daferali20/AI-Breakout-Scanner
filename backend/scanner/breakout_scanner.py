"""Main breakout scanner with pre-breakout and confirmation scoring."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from backend.analysis.indicators import TechnicalIndicators
from backend.analysis.squeeze_detector import SqueezeDetector


class BreakoutScanner:
    """Detect compression, breakout-ready setups and confirmed breakouts."""

    def __init__(self) -> None:
        self.squeeze = SqueezeDetector()
        self.indicators = TechnicalIndicators()

    def scan_stock(self, symbol: str, df: Optional[pd.DataFrame] = None) -> Dict:
        if df is None:
            try:
                df = yf.Ticker(symbol).history(period="1y", auto_adjust=False)
            except Exception as exc:
                return {"error": f"لا يمكن جلب بيانات السهم {symbol}: {exc}"}

        if df is None or df.empty or len(df) < 50:
            return {"error": f"بيانات غير كافية للسهم {symbol}"}

        try:
            df = df.copy().dropna(subset=["High", "Low", "Close", "Volume"])
            squeeze_result = self.squeeze.detect(df)
            if "error" in squeeze_result:
                return squeeze_result

            indicators = self.indicators.calculate_all(df)
            features = {**squeeze_result, **indicators, "current_price": float(df["Close"].iloc[-1])}
            score = self._calculate_score(features)
            phase = self._classify_phase(features)
            levels = self._calculate_levels(df)
            risk = self._false_breakout_risk(features)

            return {
                "symbol": symbol.upper(),
                "score": score,
                "phase": phase,
                "breakout_probability": round(self._breakout_probability(features), 2),
                "false_breakout_risk": round(risk, 2),
                "breakout_confirmed": bool(features.get("breakout_confirmed", False)),
                "squeeze": squeeze_result,
                "indicators": indicators,
                "levels": levels,
                "recommendation": self._get_recommendation(score, phase, risk),
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _calculate_score(self, x: Dict) -> float:
        """Weighted setup score. It rewards confirmation, not volatility alone."""
        squeeze = float(x.get("squeeze_score", 50))
        volume = float(x.get("volume_score", 40))
        rsi = float(x.get("rsi_score", 50))
        trend = float(x.get("trend_strength", 0.5)) * 100
        breakout = float(x.get("breakout_score", 50))
        position = float(x.get("price_position", 0.5)) * 100
        risk = self._false_breakout_risk(x)

        score = (
            squeeze * 0.18
            + volume * 0.18
            + rsi * 0.10
            + trend * 0.14
            + breakout * 0.25
            + position * 0.10
            + (100 - risk) * 0.05
        )
        return round(float(np.clip(score, 0, 100)), 2)

    @staticmethod
    def _classify_phase(x: Dict) -> str:
        confirmed = bool(x.get("breakout_confirmed", False))
        distance = float(x.get("resistance_distance", 1.0))
        rvol = float(x.get("relative_volume", x.get("volume_ratio", 1.0)))
        squeeze = bool(x.get("is_squeeze", x.get("squeeze_on", False)))
        momentum = float(x.get("momentum_5d", 0.0))
        if confirmed:
            return "BREAKOUT_CONFIRMED"
        if distance <= 0.02 and rvol >= 1.5 and momentum > 0:
            return "BREAKOUT_READY"
        if squeeze and distance <= 0.06:
            return "BUILDING"
        return "WATCH"

    @staticmethod
    def _breakout_probability(x: Dict) -> float:
        score = float(x.get("breakout_score", 50))
        trend = float(x.get("trend_strength", 0.5)) * 100
        rvol = float(x.get("relative_volume", 1.0))
        distance = float(x.get("resistance_distance", 1.0))
        probability = 0.50 * score + 0.20 * trend + 0.20 * np.clip(rvol / 2.5, 0, 1) * 100
        probability += 0.10 * np.clip(1 - distance / 0.08, 0, 1) * 100
        return float(np.clip(probability, 0, 100))

    @staticmethod
    def _false_breakout_risk(x: Dict) -> float:
        rvol = float(x.get("relative_volume", 1.0))
        trend = float(x.get("trend_strength", 0.5))
        rsi = float(x.get("rsi", 50))
        momentum = float(x.get("momentum_5d", 0.0))
        risk = 45.0
        if rvol < 1.2: risk += 20
        elif rvol >= 2.0: risk -= 12
        if trend < 0.35: risk += 18
        elif trend > 0.70: risk -= 10
        if rsi > 78: risk += 12
        if momentum < 0: risk += 15
        return float(np.clip(risk, 0, 100))

    @staticmethod
    def _calculate_levels(df: pd.DataFrame) -> Dict:
        close = pd.to_numeric(df["Close"], errors="coerce")
        high = pd.to_numeric(df["High"], errors="coerce")
        low = pd.to_numeric(df["Low"], errors="coerce")
        current = float(close.iloc[-1])
        prev_close = close.shift(1)
        tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
        atr = float(tr.ewm(alpha=1 / 14, adjust=False).mean().iloc[-1])
        atr = atr if np.isfinite(atr) and atr > 0 else current * 0.02
        resistance = float(high.iloc[-21:-1].max())
        support = float(low.iloc[-21:-1].min())
        entry = resistance + 0.10 * atr
        stop = min(current - 1.5 * atr, resistance - 1.0 * atr)
        return {
            "current": round(current, 2),
            "resistance": round(resistance, 2),
            "support": round(support, 2),
            "entry": round(entry, 2),
            "stop_loss": round(max(0, stop), 2),
            "target_1": round(current + 2 * atr, 2),
            "target_2": round(current + 3.5 * atr, 2),
            "atr": round(atr, 2),
        }

    @staticmethod
    def _get_recommendation(score: float, phase: str, risk: float) -> Dict:
        if phase == "BREAKOUT_CONFIRMED" and score >= 75 and risk < 45:
            return {"action": "🟢 اختراق مؤكد", "risk": "متوسط"}
        if phase == "BREAKOUT_READY" and score >= 70 and risk < 55:
            return {"action": "🎯 جاهز للاختراق", "risk": "متوسط"}
        if score >= 65:
            return {"action": "🟡 مراقبة قوية", "risk": "متوسط"}
        if score >= 50:
            return {"action": "🔍 مراقبة", "risk": "مرتفع"}
        return {"action": "🔴 تجنب", "risk": "مرتفع"}

    def scan_symbols(self, symbols: List[str], min_score: float = 0) -> pd.DataFrame:
        results = []
        for symbol in symbols:
            result = self.scan_stock(symbol)
            if "error" not in result and result.get("score", 0) >= min_score:
                results.append({
                    "symbol": symbol.upper(),
                    "score": result["score"],
                    "phase": result["phase"],
                    "breakout_probability": result["breakout_probability"],
                    "false_breakout_risk": result["false_breakout_risk"],
                    "squeeze": result["squeeze"].get("squeeze_score", 0),
                    "rvol": result["indicators"].get("relative_volume", 1),
                    "recommendation": result["recommendation"]["action"],
                    "risk": result["recommendation"]["risk"],
                    "price": result["levels"]["current"],
                    "target": result["levels"]["target_1"],
                })
        return pd.DataFrame(results).sort_values("score", ascending=False) if results else pd.DataFrame()

    def scan_market(self, symbols: List[str], min_score: float = 60) -> pd.DataFrame:
        """Backward-compatible market scan without DataFrame truth-value errors."""
        return self.scan_symbols(symbols, min_score=min_score)
