"""Market phase detection using normalized technical and liquidity features."""

from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import numpy as np

from .models import INDICATOR_WEIGHTS, MarketPhase, PhaseMetrics


class PhaseDetector:
    def __init__(self) -> None:
        self.phase_thresholds = {
            MarketPhase.ACCUMULATION: {
                "volume_trend": (0.7, 1.2), "price_position": (0.20, 0.65), "volatility": (0.01, 0.06)
            },
            MarketPhase.COMPRESSION: {
                "bollinger_width": (0.0, 0.08), "atr_ratio": (0.0, 0.035), "volume_trend": (0.6, 1.5)
            },
            MarketPhase.MOMENTUM: {
                "rsi": (55, 75), "price_momentum": (1.02, 1.10), "volume_trend": (1.3, 4.0)
            },
            MarketPhase.BREAKOUT_READY: {
                "resistance_distance": (0.0, 0.025), "volume_spike": (1.2, 5.0), "bollinger_width": (0.0, 0.12)
            },
            MarketPhase.BREAKOUT: {
                "price_change": (0.02, 0.20), "volume_spike": (1.5, 8.0), "resistance_break": (1.0, 1.10)
            },
            MarketPhase.TREND_CONTINUATION: {
                "trend_strength": (0.6, 1.0), "volume_trend": (0.9, 3.0), "price_trend": (0.01, 0.20)
            },
            MarketPhase.DISTRIBUTION: {
                "volume_trend": (0.5, 1.3), "price_position": (0.70, 1.0), "volatility": (0.02, 0.08)
            },
            MarketPhase.DECLINE: {
                "price_change": (-0.20, -0.02), "volume_trend": (1.0, 4.0), "rsi": (20, 45)
            },
        }

    def detect_phase(self, data: Dict[str, Any]) -> Tuple[MarketPhase, float]:
        scores = {phase: self._calculate_phase_score(data, rules) for phase, rules in self.phase_thresholds.items()}
        best_phase = max(scores, key=scores.get)
        confidence = float(np.clip(scores[best_phase] * 100, 0, 100))
        return best_phase, confidence

    def _calculate_phase_score(self, data: Dict[str, Any], thresholds: Dict[str, Tuple[float, float]]) -> float:
        score = 0.0
        total_weight = 0.0
        for indicator, (low, high) in thresholds.items():
            value = data.get(indicator, 0)
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0
            if not np.isfinite(value):
                value = 0.0
            span = max(high - low, 1e-9)
            if low <= value <= high:
                match = 1.0 - abs(value - (low + high) / 2) / (span / 2)
            elif value < low:
                match = max(0.0, 1.0 - (low - value) / max(abs(low), span))
            else:
                match = max(0.0, 1.0 - (value - high) / max(abs(high), span))
            weight = INDICATOR_WEIGHTS.get(indicator, 0.10)
            score += match * weight
            total_weight += weight
        return score / total_weight if total_weight else 0.0

    def get_phase_metrics(self, data: Dict[str, Any], symbol: str) -> PhaseMetrics:
        phase, confidence = self.detect_phase(data)
        days = self._estimate_days_in_phase(data, phase)
        return PhaseMetrics(
            phase=phase,
            start_date=datetime.now() - timedelta(days=days),
            days_in_phase=days,
            confidence=confidence,
            probability_next=0.0,
            indicators=data,
        )

    @staticmethod
    def _estimate_days_in_phase(data: Dict[str, Any], phase: MarketPhase) -> int:
        avg = {
            MarketPhase.ACCUMULATION: 14, MarketPhase.COMPRESSION: 10, MarketPhase.MOMENTUM: 7,
            MarketPhase.BREAKOUT_READY: 3, MarketPhase.BREAKOUT: 5, MarketPhase.TREND_CONTINUATION: 12,
            MarketPhase.DISTRIBUTION: 10, MarketPhase.DECLINE: 15,
        }.get(phase, 10)
        rvol = float(data.get("volume_trend", 1.0) or 1.0)
        if rvol > 2.0: avg -= 2
        elif rvol < 0.8: avg += 2
        return max(1, int(avg))
