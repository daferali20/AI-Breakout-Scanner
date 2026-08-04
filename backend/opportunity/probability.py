from typing import Dict, Any
from .models import MarketPhase

class ProbabilityCalculator:
    def calculate_success_probability(self, phase: MarketPhase,
                                     catalysts: Dict[str, Any],
                                     data: Dict[str, Any]) -> float:
        base_prob = self._get_base_probability(phase)
        adjustments = 0
        total_catalysts = catalysts.get('total_catalysts', 0)
        adjustments += min(15, total_catalysts * 2)
        if data.get('volume_trend', 1) > 2:
            adjustments += 10
        elif data.get('volume_trend', 1) > 1.5:
            adjustments += 5
        if data.get('market_regime', 0.5) > 0.6:
            adjustments += 5
        if data.get('pattern_score', 0) > 0.7:
            adjustments += 8
        if data.get('volatility', 0.5) > 0.7:
            adjustments -= 5
        probability = min(98, max(10, base_prob + adjustments))
        return probability
    
    def _get_base_probability(self, phase: MarketPhase) -> float:
        base_probs = {
            MarketPhase.ACCUMULATION: 65, MarketPhase.COMPRESSION: 75,
            MarketPhase.MOMENTUM: 70, MarketPhase.BREAKOUT_READY: 80,
            MarketPhase.BREAKOUT: 60, MarketPhase.TREND_CONTINUATION: 55,
            MarketPhase.DISTRIBUTION: 30, MarketPhase.DECLINE: 15,
        }
        return base_probs.get(phase, 50)
