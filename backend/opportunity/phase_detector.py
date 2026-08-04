import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from .models import MarketPhase, PhaseMetrics, INDICATOR_WEIGHTS

class PhaseDetector:
    def __init__(self):
        self.phase_thresholds = {
            MarketPhase.ACCUMULATION: {'volume_trend': (0.6, 0.8), 'price_position': (0.2, 0.4), 'volatility': (0.1, 0.3)},
            MarketPhase.COMPRESSION: {'bollinger_width': (0.0, 0.3), 'atr_ratio': (0.0, 0.4), 'volume_trend': (0.8, 1.2)},
            MarketPhase.MOMENTUM: {'rsi': (60, 80), 'price_momentum': (1.02, 1.10), 'volume_trend': (1.5, 3.0)},
            MarketPhase.BREAKOUT_READY: {'resistance_distance': (0.0, 0.03), 'volume_spike': (1.8, 5.0), 'bollinger_width': (0.2, 0.5)},
            MarketPhase.BREAKOUT: {'price_change': (0.03, 0.15), 'volume_spike': (2.0, 6.0), 'resistance_break': (1.02, 1.10)},
            MarketPhase.TREND_CONTINUATION: {'trend_strength': (0.6, 1.0), 'adx': (25, 100), 'volume_trend': (1.0, 2.0)},
            MarketPhase.DISTRIBUTION: {'volume_trend': (0.4, 0.7), 'price_position': (0.7, 0.9), 'volatility': (0.2, 0.5)},
            MarketPhase.DECLINE: {'price_change': (-0.15, -0.03), 'volume_trend': (1.2, 2.5), 'rsi': (20, 40)},
        }
    
    def detect_phase(self, data: Dict[str, Any]) -> Tuple[MarketPhase, float]:
        scores = {}
        for phase, thresholds in self.phase_thresholds.items():
            score = self._calculate_phase_score(data, thresholds)
            scores[phase] = score
        best_phase = max(scores, key=scores.get)
        confidence = scores[best_phase] * 100
        return best_phase, min(confidence, 100.0)
    
    def _calculate_phase_score(self, data: Dict[str, Any], thresholds: Dict) -> float:
        score = 0.0
        total_weight = 0
        for indicator, (low, high) in thresholds.items():
            value = data.get(indicator, 0)
            if low <= value <= high:
                mid = (low + high) / 2
                if high - low > 0:
                    match = 1 - abs(value - mid) / ((high - low) / 2)
                else:
                    match = 1.0
            else:
                if value < low:
                    match = max(0, 1 - (low - value) / low)
                else:
                    match = max(0, 1 - (value - high) / high)
            weight = INDICATOR_WEIGHTS.get(indicator, 0.1)
            score += match * weight
            total_weight += weight
        return score / total_weight if total_weight > 0 else 0
    
    def get_phase_metrics(self, data: Dict[str, Any], symbol: str) -> PhaseMetrics:
        phase, confidence = self.detect_phase(data)
        days_in_phase = self._estimate_days_in_phase(data, phase)
        start_date = datetime.now() - timedelta(days=days_in_phase)
        return PhaseMetrics(
            phase=phase,
            start_date=start_date,
            days_in_phase=days_in_phase,
            confidence=confidence,
            probability_next=0.0,
            indicators=data
        )
    
    def _estimate_days_in_phase(self, data: Dict[str, Any], phase: MarketPhase) -> int:
        avg_duration = {
            MarketPhase.ACCUMULATION: 14, MarketPhase.COMPRESSION: 10,
            MarketPhase.MOMENTUM: 7, MarketPhase.BREAKOUT_READY: 3,
            MarketPhase.BREAKOUT: 5, MarketPhase.TREND_CONTINUATION: 12,
            MarketPhase.DISTRIBUTION: 10, MarketPhase.DECLINE: 15,
        }.get(phase, 10)
        volatility = data.get('volatility', 0.5)
        if volatility < 0.3:
            days = avg_duration + 3
        elif volatility > 0.7:
            days = avg_duration - 2
        else:
            days = avg_duration
        return max(1, int(days))
