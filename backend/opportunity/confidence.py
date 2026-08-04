from typing import Dict, Any
import numpy as np
from .models import PhaseMetrics

class ConfidenceCalculator:
    def calculate(self, phase_metrics: PhaseMetrics, 
                 data: Dict[str, Any], catalyst_summary: Dict[str, Any]) -> float:
        confidence_components = []
        weights = []
        tech_score = self._calculate_technical_confidence(data)
        confidence_components.append(tech_score)
        weights.append(0.30)
        catalyst_score = self._calculate_catalyst_confidence(catalyst_summary)
        confidence_components.append(catalyst_score)
        weights.append(0.25)
        phase_stability = self._calculate_phase_stability(phase_metrics, data)
        confidence_components.append(phase_stability)
        weights.append(0.20)
        alignment_score = self._calculate_alignment(data)
        confidence_components.append(alignment_score)
        weights.append(0.15)
        historical_score = self._calculate_historical_confidence(phase_metrics)
        confidence_components.append(historical_score)
        weights.append(0.10)
        total_confidence = np.average(confidence_components, weights=weights)
        return min(100.0, total_confidence * 100)
    
    def _calculate_technical_confidence(self, data: Dict[str, Any]) -> float:
        scores = []
        indicators = [('bollinger_width', 0.3, 1.0), ('atr_ratio', 0.4, 1.0), ('volume_trend', 1.5, 0.0)]
        for indicator, optimal, inverse in indicators:
            value = data.get(indicator, 0.5)
            if inverse:
                if value <= optimal:
                    score = 1.0
                else:
                    score = max(0, 1 - (value - optimal) / optimal)
            else:
                if value >= optimal:
                    score = 1.0
                else:
                    score = max(0, value / optimal)
            scores.append(score)
        return np.mean(scores) if scores else 0.5
    
    def _calculate_catalyst_confidence(self, catalyst_summary: Dict[str, Any]) -> float:
        total = catalyst_summary.get('total_catalysts', 0)
        if total >= 7:
            return 1.0
        elif total >= 5:
            return 0.85
        elif total >= 3:
            return 0.65
        elif total >= 1:
            return 0.40
        else:
            return 0.20
    
    def _calculate_phase_stability(self, phase_metrics: PhaseMetrics, data: Dict[str, Any]) -> float:
        days = phase_metrics.days_in_phase
        if days <= 3:
            stability = 0.3
        elif days <= 7:
            stability = 0.6
        elif days <= 14:
            stability = 0.85
        elif days <= 21:
            stability = 1.0
        else:
            stability = 0.9
        volatility = data.get('volatility', 0.5)
        if volatility < 0.3:
            stability *= 1.1
        elif volatility > 0.7:
            stability *= 0.8
        return min(1.0, stability)
    
    def _calculate_alignment(self, data: Dict[str, Any]) -> float:
        indicators = [
            data.get('bollinger_width', 0.5), data.get('atr_ratio', 0.5),
            data.get('volume_trend', 1.0), data.get('trend_strength', 0.5),
            data.get('rsi', 50), data.get('smart_money_flow', 0.5),
        ]
        normalized = []
        for i, val in enumerate(indicators):
            if i in [0, 1]:
                norm = 1 - min(1, val)
            elif i in [2, 3]:
                norm = min(1, val / 2)
            elif i == 4:
                norm = 1 - abs(val - 50) / 50
            else:
                norm = val
            normalized.append(norm)
        variance = np.var(normalized)
        alignment = max(0, 1 - variance * 2)
        return min(1.0, alignment)
    
    def _calculate_historical_confidence(self, phase_metrics: PhaseMetrics) -> float:
        days = phase_metrics.days_in_phase
        if days < 3:
            return 0.3
        elif days < 7:
            return 0.5
        elif days < 14:
            return 0.7
        else:
            return 0.85
