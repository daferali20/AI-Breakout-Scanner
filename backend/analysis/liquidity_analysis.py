"""
تحليل السيولة - مع دمج مؤشرات الضغط
"""

from typing import Dict, Any
import numpy as np

from backend.opportunity import MarketPhase, PhaseDetector


class LiquidityAnalyzer:
    """محلل السيولة المتقدم"""
    
    def __init__(self):
        self.phase_detector = PhaseDetector()
    
    def analyze_liquidity(self, price_data: Dict[str, Any], 
                         volume_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل السيولة مع تحديد مرحلة الضغط"""
        
        # المؤشرات الأساسية
        bollinger_width = self._calculate_bollinger_width(price_data)
        atr_ratio = self._calculate_atr_ratio(price_data)
        volume_trend = self._calculate_volume_trend(volume_data)
        smart_money_flow = self._calculate_smart_money(price_data, volume_data)
        
        # تجميع البيانات
        data = {
            'bollinger_width': bollinger_width,
            'atr_ratio': atr_ratio,
            'volume_trend': volume_trend,
            'smart_money_flow': smart_money_flow,
            'volatility': np.std(price_data.get('close', [0])[-20:]),
            'trend_strength': self._calculate_trend_strength(price_data),
        }
        
        # كشف المرحلة
        phase_metrics = self.phase_detector.get_phase_metrics(data, '')
        
        return {
            'bollinger_width': bollinger_width,
            'atr_ratio': atr_ratio,
            'volume_trend': volume_trend,
            'smart_money_flow': smart_money_flow,
            'phase': phase_metrics.phase,
            'phase_days': phase_metrics.days_in_phase,
            'is_compressed': bollinger_width < 0.3 and atr_ratio < 0.4,
            'compression_level': 1 - bollinger_width,
        }
    
    def _calculate_bollinger_width(self, data: Dict) -> float:
        """حساب عرض نطاق بولينجر"""
        # محاكاة
        return 0.27
    
    def _calculate_atr_ratio(self, data: Dict) -> float:
        """حساب نسبة ATR"""
        return 0.35
    
    def _calculate_volume_trend(self, data: Dict) -> float:
        """حساب اتجاه الحجم"""
        return 2.4
    
    def _calculate_smart_money(self, price, volume) -> float:
        """حساب تدفقات Smart Money"""
        return 0.68
    
    def _calculate_trend_strength(self, data: Dict) -> float:
        """حساب قوة الاتجاه"""
        return 0.75
