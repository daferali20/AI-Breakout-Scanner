"""
تحديد المرحلة الحالية للسهم
"""

import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd

from .models import MarketPhase, PhaseMetrics, INDICATOR_WEIGHTS


class PhaseDetector:
    """كاشف مراحل السوق"""
    
    def __init__(self):
        self.phase_thresholds = {
            MarketPhase.ACCUMULATION: {
                'volume_trend': (0.6, 0.8),  # حجم منخفض إلى متوسط
                'price_position': (0.2, 0.4),  # قرب القاع
                'volatility': (0.1, 0.3),  # تقلبات منخفضة
            },
            MarketPhase.COMPRESSION: {
                'bollinger_width': (0.0, 0.3),  # نطاق ضيق جداً
                'atr_ratio': (0.0, 0.4),  # ATR منخفض
                'volume_trend': (0.8, 1.2),  # حجم قريب من المتوسط
            },
            MarketPhase.MOMENTUM: {
                'rsi': (60, 80),  # RSI مرتفع
                'price_momentum': (1.02, 1.10),  # زخم إيجابي
                'volume_trend': (1.5, 3.0),  # حجم عالي
            },
            MarketPhase.BREAKOUT_READY: {
                'resistance_distance': (0.0, 0.03),  # قرب المقاومة
                'volume_spike': (1.8, 5.0),  # قفزة حجمية
                'bollinger_width': (0.2, 0.5),  # بداية توسع النطاق
            },
            MarketPhase.BREAKOUT: {
                'price_change': (0.03, 0.15),  # تغير سعري كبير
                'volume_spike': (2.0, 6.0),  # حجم ضخم
                'resistance_break': (1.02, 1.10),  # كسر المقاومة
            },
            MarketPhase.TREND_CONTINUATION: {
                'trend_strength': (0.6, 1.0),  # قوة الاتجاه
                'adx': (25, 100),  # ADX قوي
                'volume_trend': (1.0, 2.0),  # حجم مستمر
            },
            MarketPhase.DISTRIBUTION: {
                'volume_trend': (0.4, 0.7),  # حجم منخفض
                'price_position': (0.7, 0.9),  # قرب القمة
                'volatility': (0.2, 0.5),  # تقلبات متوسطة
            },
            MarketPhase.DECLINE: {
                'price_change': (-0.15, -0.03),  # تغير سلبي
                'volume_trend': (1.2, 2.5),  # حجم مرتفع في الهبوط
                'rsi': (20, 40),  # RSI منخفض
            }
        }
    
    def detect_phase(self, data: Dict[str, Any]) -> Tuple[MarketPhase, float]:
        """
        تحديد المرحلة الحالية مع درجة الثقة
        
        Args:
            data: بيانات السهم المحللة
        
        Returns:
            Tuple[MarketPhase, float]: المرحلة ودرجة الثقة
        """
        scores = {}
        
        for phase, thresholds in self.phase_thresholds.items():
            score = self._calculate_phase_score(data, thresholds)
            scores[phase] = score
        
        # اختيار المرحلة الأعلى درجة
        best_phase = max(scores, key=scores.get)
        confidence = scores[best_phase] * 100
        
        return best_phase, min(confidence, 100.0)
    
    def _calculate_phase_score(self, data: Dict[str, Any], thresholds: Dict) -> float:
        """حساب درجة تطابق المرحلة"""
        score = 0.0
        total_weight = 0
        
        for indicator, (low, high) in thresholds.items():
            value = data.get(indicator, 0)
            
            # حساب درجة التطابق
            if low <= value <= high:
                # كلما كان في منتصف النطاق كانت الدرجة أعلى
                mid = (low + high) / 2
                if high - low > 0:
                    match = 1 - abs(value - mid) / ((high - low) / 2)
                else:
                    match = 1.0
            else:
                # خارج النطاق
                if value < low:
                    match = max(0, 1 - (low - value) / low)
                else:
                    match = max(0, 1 - (value - high) / high)
            
            # تطبيق الوزن
            weight = INDICATOR_WEIGHTS.get(indicator, 0.1)
            score += match * weight
            total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0
    
    def get_phase_metrics(self, data: Dict[str, Any], symbol: str) -> PhaseMetrics:
        """الحصول على مقاييس المرحلة الكاملة"""
        phase, confidence = self.detect_phase(data)
        
        # تقدير بداية المرحلة
        days_in_phase = self._estimate_days_in_phase(data, phase)
        start_date = datetime.now() - timedelta(days=days_in_phase)
        
        return PhaseMetrics(
            phase=phase,
            start_date=start_date,
            days_in_phase=days_in_phase,
            confidence=confidence,
            probability_next=0.0,  # سيتم حسابه لاحقاً
            indicators=data
        )
    
    def _estimate_days_in_phase(self, data: Dict[str, Any], phase: MarketPhase) -> int:
        """تقدير عدد الأيام في المرحلة الحالية"""
        # يعتمد على بيانات تاريخية
        avg_duration = {
            MarketPhase.ACCUMULATION: 14,
            MarketPhase.COMPRESSION: 10,
            MarketPhase.MOMENTUM: 7,
            MarketPhase.BREAKOUT_READY: 3,
            MarketPhase.BREAKOUT: 5,
            MarketPhase.TREND_CONTINUATION: 12,
            MarketPhase.DISTRIBUTION: 10,
            MarketPhase.DECLINE: 15,
        }.get(phase, 10)
        
        # محاكاة بناءً على المؤشرات
        volatility = data.get('volatility', 0.5)
        if volatility < 0.3:
            days = avg_duration + 3  # تقلبات أقل = فترة أطول
        elif volatility > 0.7:
            days = avg_duration - 2  # تقلبات عالية = فترة أقصر
        else:
            days = avg_duration
        
        return max(1, int(days))
