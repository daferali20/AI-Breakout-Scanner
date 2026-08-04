"""
حساب درجة الفرصة الاستثمارية
"""

from typing import Dict, Any
import numpy as np

from .models import PhaseMetrics, MarketPhase


class OpportunityScorer:
    """حاسبة درجة الفرصة"""
    
    def calculate_score(self, phase_metrics: PhaseMetrics,
                       catalyst_summary: Dict[str, Any],
                       data: Dict[str, Any]) -> float:
        """حساب درجة الفرصة الإجمالية"""
        
        # 1. جودة المرحلة (30%)
        phase_score = self._score_phase(phase_metrics.phase, data)
        
        # 2. قوة المحفزات (25%)
        catalyst_score = self._score_catalysts(catalyst_summary)
        
        # 3. احتمالية الانتقال (20%)
        transition_score = phase_metrics.probability_next * 100
        
        # 4. الثقة (15%)
        confidence_score = phase_metrics.confidence
        
        # 5. الزخم (10%)
        momentum_score = self._score_momentum(data)
        
        # حساب المتوسط المرجح
        total_score = (
            phase_score * 0.30 +
            catalyst_score * 0.25 +
            transition_score * 0.20 +
            confidence_score * 0.15 +
            momentum_score * 0.10
        )
        
        # ضبط النتيجة
        return min(100.0, max(0.0, total_score))
    
    def _score_phase(self, phase: MarketPhase, data: Dict[str, Any]) -> float:
        """حساب درجة المرحلة"""
        phase_scores = {
            MarketPhase.ACCUMULATION: 85,
            MarketPhase.COMPRESSION: 90,
            MarketPhase.MOMENTUM: 80,
            MarketPhase.BREAKOUT_READY: 95,
            MarketPhase.BREAKOUT: 75,
            MarketPhase.TREND_CONTINUATION: 70,
            MarketPhase.DISTRIBUTION: 40,
            MarketPhase.DECLINE: 20,
        }
        
        base_score = phase_scores.get(phase, 50)
        
        # تعديل حسب بيانات إضافية
        adjustment = 0
        
        # قوة المرحلة الحالية
        if data.get('trend_strength', 0.5) > 0.7:
            adjustment += 5
        
        if data.get('volume_trend', 1) > 1.5:
            adjustment += 3
        
        if data.get('bollinger_width', 1) < 0.3:
            adjustment += 5
        
        return min(100, max(0, base_score + adjustment))
    
    def _score_catalysts(self, catalyst_summary: Dict[str, Any]) -> float:
        """حساب درجة المحفزات"""
        total = catalyst_summary.get('total_catalysts', 0)
        
        if total >= 8:
            return 95
        elif total >= 6:
            return 85
        elif total >= 4:
            return 70
        elif total >= 2:
            return 50
        elif total >= 1:
            return 35
        else:
            return 20
    
    def _score_momentum(self, data: Dict[str, Any]) -> float:
        """حساب درجة الزخم"""
        scores = []
        
        # اتجاه السعر
        price_trend = data.get('price_trend', 0)
        if price_trend > 0.05:
            scores.append(90)
        elif price_trend > 0.02:
            scores.append(70)
        elif price_trend > 0:
            scores.append(50)
        else:
            scores.append(30)
        
        # RSI
        rsi = data.get('rsi', 50)
        if 55 <= rsi <= 70:
            scores.append(85)  # منطقة الزخم المثالي
        elif 45 <= rsi <= 80:
            scores.append(65)
        else:
            scores.append(40)
        
        # حجم
        volume = data.get('volume_trend', 1)
        if volume > 2:
            scores.append(90)
        elif volume > 1.5:
            scores.append(70)
        else:
            scores.append(50)
        
        return np.mean(scores) if scores else 50
