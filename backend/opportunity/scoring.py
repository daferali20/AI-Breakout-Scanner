"""Explainable opportunity scoring."""

from typing import Any, Dict

import numpy as np

from .models import MarketPhase, PhaseMetrics


class OpportunityScorer:
    def calculate_score(self, phase_metrics: PhaseMetrics, catalyst_summary: Dict[str, Any], data: Dict[str, Any]) -> float:
        phase_score = self._score_phase(phase_metrics.phase, data)
        catalyst_score = self._score_catalysts(catalyst_summary)
        transition_score = float(np.clip(phase_metrics.probability_next, 0, 1)) * 100
        confidence_score = float(np.clip(phase_metrics.confidence, 0, 100))
        momentum_score = self._score_momentum(data)
        breakout_score = float(np.clip(data.get("breakout_score", 50), 0, 100))
        liquidity_score = float(np.clip(data.get("smart_money_score", 50), 0, 100))

        total = (
            phase_score * 0.20
            + catalyst_score * 0.15
            + transition_score * 0.15
            + confidence_score * 0.10
            + momentum_score * 0.10
            + breakout_score * 0.20
            + liquidity_score * 0.10
        )
        return float(np.clip(total, 0, 100))

    @staticmethod
    def _score_phase(phase: MarketPhase, data: Dict[str, Any]) -> float:
        phase_scores = {
            MarketPhase.ACCUMULATION: 75,
            MarketPhase.COMPRESSION: 88,
            MarketPhase.MOMENTUM: 82,
            MarketPhase.BREAKOUT_READY: 94,
            MarketPhase.BREAKOUT: 90,
            MarketPhase.TREND_CONTINUATION: 78,
            MarketPhase.DISTRIBUTION: 35,
            MarketPhase.DECLINE: 15,
        }
        score = phase_scores.get(phase, 50)
        if float(data.get("trend_strength", 0.5)) > 0.7: score += 4
        if float(data.get("volume_trend", 1.0)) > 1.5: score += 4
        if float(data.get("resistance_distance", 1.0)) <= 0.025: score += 4
        return float(np.clip(score, 0, 100))

    @staticmethod
    def _score_catalysts(catalyst_summary: Dict[str, Any]) -> float:
        total = int(catalyst_summary.get("total_catalysts", 0))
        return {0: 20, 1: 35, 2: 50, 3: 60, 4: 70, 5: 78, 6: 85}.get(total, 95)

    @staticmethod
    def _score_momentum(data: Dict[str, Any]) -> float:
        price_trend = float(data.get("price_trend", 0) or 0)
        rsi = float(data.get("rsi", 50) or 50)
        volume = float(data.get("volume_trend", 1) or 1)
        price_score = 90 if price_trend > 0.05 else 75 if price_trend > 0.02 else 55 if price_trend > 0 else 30
        rsi_score = 90 if 55 <= rsi <= 70 else 70 if 45 <= rsi <= 78 else 40
        volume_score = 90 if volume > 2 else 75 if volume > 1.5 else 50
        return float(np.mean([price_score, rsi_score, volume_score]))
