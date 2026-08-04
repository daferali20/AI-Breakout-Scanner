"""
نموذج توقع الانتقال للمرحلة التالية
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from datetime import datetime, timedelta

from .models import MarketPhase, PHASE_PROPERTIES


class TransitionModel:
    """نموذج توقع انتقال المراحل"""
    
    def __init__(self):
        # مصفوفة الانتقال (احتمالات الانتقال بين المراحل)
        self.transition_matrix = self._build_transition_matrix()
    
    def _build_transition_matrix(self) -> Dict[MarketPhase, Dict[MarketPhase, float]]:
        """بناء مصفوفة انتقال المراحل"""
        matrix = {}
        
        for phase in MarketPhase:
            matrix[phase] = {}
            next_phases = PHASE_PROPERTIES.get(phase, {}).get('next_phases', [])
            
            if next_phases:
                prob = 1.0 / len(next_phases)
                for next_phase in next_phases:
                    matrix[phase][next_phase] = prob
            else:
                # حالة نهاية، العودة للبداية
                matrix[phase][MarketPhase.ACCUMULATION] = 1.0
        
        return matrix
    
    def predict_next_phase(self, current_phase: MarketPhase, 
                          indicators: Dict[str, Any]) -> Tuple[MarketPhase, float, int]:
        """
        توقع المرحلة التالية مع الاحتمالية والأيام المتوقعة
        
        Returns:
            Tuple[MarketPhase, float, int]: المرحلة التالية، الاحتمالية، الأيام المتوقعة
        """
        # الحصول على المراحل المحتملة
        possible_phases = PHASE_PROPERTIES.get(current_phase, {}).get('next_phases', [])
        
        if not possible_phases:
            return MarketPhase.ACCUMULATION, 0.5, 14
        
        # حساب درجات كل مرحلة محتملة
        scores = {}
        for phase in possible_phases:
            score = self._calculate_transition_score(current_phase, phase, indicators)
            scores[phase] = score
        
        # اختيار أفضل مرحلة
        best_phase = max(scores, key=scores.get)
        probability = scores[best_phase]
        
        # تقدير الأيام
        expected_days = self._estimate_days_to_transition(current_phase, best_phase, indicators)
        
        return best_phase, probability, expected_days
    
    def _calculate_transition_score(self, from_phase: MarketPhase, 
                                   to_phase: MarketPhase, 
                                   indicators: Dict[str, Any]) -> float:
        """حساب درجة الانتقال بين مرحلتين"""
        score = 1.0
        
        # عوامل تساعد على الانتقال
        catalysts = 0
        
        # 1. زيادة الحجم
        if indicators.get('volume_trend', 0) > 1.5:
            catalysts += 0.2
        
        # 2. تضيق النطاق
        if indicators.get('bollinger_width', 1) < 0.3:
            catalysts += 0.2
        
        # 3. قوة الاتجاه
        if indicators.get('trend_strength', 0) > 0.6:
            catalysts += 0.2
        
        # 4. اختراق المقاومة
        if indicators.get('resistance_break', 0) > 1.02:
            catalysts += 0.25
        
        # 5. محفزات إخبارية
        if indicators.get('news_sentiment', 0) > 0.6:
            catalysts += 0.15
        
        # تطبيق المحفزات على الاحتمال الأساسي
        base_prob = self.transition_matrix.get(from_phase, {}).get(to_phase, 0.3)
        adjusted_prob = min(base_prob + catalysts, 0.98)
        
        return adjusted_prob
    
    def _estimate_days_to_transition(self, from_phase: MarketPhase, 
                                     to_phase: MarketPhase,
                                     indicators: Dict[str, Any]) -> int:
        """تقدير عدد الأيام حتى الانتقال"""
        # المدة الأساسية
        base_days = PHASE_PROPERTIES.get(from_phase, {}).get('avg_duration', 7)
        
        # تعديل المدة بناءً على المؤشرات
        adjustments = 0
        
        # حجم أعلى = انتقال أسرع
        if indicators.get('volume_trend', 0) > 2.0:
            adjustments -= 2
        elif indicators.get('volume_trend', 0) < 0.8:
            adjustments += 2
        
        # تضيق النطاق = انتقال أسرع
        if indicators.get('bollinger_width', 1) < 0.2:
            adjustments -= 1
        elif indicators.get('bollinger_width', 1) > 0.5:
            adjustments += 1
        
        # قوة الاتجاه = انتقال أسرع
        if indicators.get('trend_strength', 0) > 0.7:
            adjustments -= 1
        
        # التعديل النهائي
        days = max(1, base_days + adjustments)
        
        # تحديد نطاق زمني معقول
        if from_phase == MarketPhase.COMPRESSION:
            days = max(3, min(7, days))
        elif from_phase == MarketPhase.BREAKOUT_READY:
            days = max(1, min(3, days))
        
        return days
