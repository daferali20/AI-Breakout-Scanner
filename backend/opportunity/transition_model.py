"""Rule-based transition model calibrated to normalized market features."""

from typing import Any, Dict, Tuple

from .models import MarketPhase, PHASE_PROPERTIES


class TransitionModel:
    """Estimate the next market phase from current phase and live features."""

    def __init__(self) -> None:
        self.transition_matrix = self._build_transition_matrix()

    def _build_transition_matrix(self) -> Dict[MarketPhase, Dict[MarketPhase, float]]:
        matrix: Dict[MarketPhase, Dict[MarketPhase, float]] = {}
        for phase in MarketPhase:
            next_phases = PHASE_PROPERTIES.get(phase, {}).get("next_phases", [])
            if next_phases:
                base = 1.0 / len(next_phases)
                matrix[phase] = {next_phase: base for next_phase in next_phases}
            else:
                matrix[phase] = {MarketPhase.ACCUMULATION: 1.0}
        return matrix

    def predict_next_phase(
        self, current_phase: MarketPhase, indicators: Dict[str, Any]
    ) -> Tuple[MarketPhase, float, int]:
        possible = PHASE_PROPERTIES.get(current_phase, {}).get("next_phases", [])
        if not possible:
            return MarketPhase.ACCUMULATION, 0.5, 14
        scores = {
            phase: self._calculate_transition_score(current_phase, phase, indicators)
            for phase in possible
        }
        best = max(scores, key=scores.get)
        return best, float(min(scores[best], 0.98)), self._estimate_days_to_transition(current_phase, indicators)

    def _calculate_transition_score(self, from_phase: MarketPhase, to_phase: MarketPhase, indicators: Dict[str, Any]) -> float:
        base = self.transition_matrix.get(from_phase, {}).get(to_phase, 0.3)
        boost = 0.0
        rvol = float(indicators.get("volume_trend", 1.0) or 1.0)
        bb = float(indicators.get("bollinger_width", 1.0) or 1.0)
        trend = float(indicators.get("trend_strength", 0.5) or 0.5)
        resistance = float(indicators.get("resistance_break", 1.0) or 1.0)
        sentiment = float(indicators.get("news_sentiment", 0.0) or 0.0)
        breakout = bool(indicators.get("breakout_confirmed", False))

        if rvol >= 1.5: boost += 0.12
        if bb <= 0.08: boost += 0.10
        if trend >= 0.65: boost += 0.10
        if resistance >= 1.0: boost += 0.15
        if sentiment > 0.6: boost += 0.08
        if breakout and to_phase in (MarketPhase.BREAKOUT, MarketPhase.TREND_CONTINUATION): boost += 0.15
        if to_phase == MarketPhase.BREAKOUT_READY and indicators.get("resistance_distance", 1) <= 0.025: boost += 0.12

        return min(base + boost, 0.98)

    @staticmethod
    def _estimate_days_to_transition(current_phase: MarketPhase, indicators: Dict[str, Any]) -> int:
        base = PHASE_PROPERTIES.get(current_phase, {}).get("avg_duration", 7)
        rvol = float(indicators.get("volume_trend", 1.0) or 1.0)
        trend = float(indicators.get("trend_strength", 0.5) or 0.5)
        days = base - (2 if rvol > 2 else 1 if rvol > 1.5 else 0) - (1 if trend > 0.7 else 0)
        if current_phase == MarketPhase.COMPRESSION:
            return max(2, min(7, days))
        if current_phase == MarketPhase.BREAKOUT_READY:
            return max(1, min(3, days))
        return max(1, int(days))
