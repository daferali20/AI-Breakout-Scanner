"""Explainable AI-style opportunity scoring built from live market features."""

from typing import Any, Dict

import numpy as np

from backend.opportunity import OpportunityEngine


class AIScoreAnalyzer:
    """Produce explainable scores from live features and the opportunity engine."""

    def __init__(self) -> None:
        self.opportunity_engine = OpportunityEngine()

    def analyze(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        base = self._feature_analysis(data)
        opportunity = self.opportunity_engine.analyze(symbol, data)
        combined = float(np.clip(0.65 * opportunity.opportunity_score + 0.35 * base["technical_score"] * 100, 0, 100))
        return {
            **base,
            "opportunity": opportunity,
            "ai_confidence": round(float(opportunity.confidence), 2),
            "ai_score": round(combined, 2),
            "recommendation": self._get_recommendation(combined),
            "score_type": "explainable_rule_based_baseline",
        }

    @staticmethod
    def _feature_analysis(data: Dict[str, Any]) -> Dict[str, float]:
        rsi = float(data.get("rsi", 50) or 50)
        rvol = float(data.get("relative_volume", data.get("volume_trend", 1)) or 1)
        trend = float(data.get("trend_strength", 0.5) or 0.5)
        squeeze = float(data.get("squeeze_score", 50) or 50) / 100
        momentum = float(data.get("price_trend", 0) or 0)
        technical = (
            0.25 * np.clip(1 - abs(rsi - 60) / 40, 0, 1)
            + 0.25 * np.clip(rvol / 2.5, 0, 1)
            + 0.25 * np.clip(trend, 0, 1)
            + 0.15 * squeeze
            + 0.10 * np.clip((momentum + 0.05) / 0.10, 0, 1)
        )
        return {
            "technical_score": round(float(np.clip(technical, 0, 1)), 4),
            "fundamental_score": float(np.clip(data.get("fundamental_score", 0.5), 0, 1)),
            "sentiment_score": float(np.clip(data.get("sentiment_score", 0.5), 0, 1)),
        }

    @staticmethod
    def _get_recommendation(score: float) -> str:
        if score >= 80: return "قوي جداً"
        if score >= 70: return "قوي"
        if score >= 60: return "إيجابي"
        if score >= 45: return "محايد"
        return "تجنب"
