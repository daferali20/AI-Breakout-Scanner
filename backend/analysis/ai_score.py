"""
AI Score - تحليل متقدم باستخدام الذكاء الاصطناعي
"""

from typing import Dict, Any
import numpy as np

# إضافة استيراد المحرك الجديد
from backend.opportunity import OpportunityEngine


class AIScoreAnalyzer:
    """محلل درجات الذكاء الاصطناعي"""
    
    def __init__(self):
        self.opportunity_engine = OpportunityEngine()
    
    def analyze(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحليل شامل باستخدام AI
        
        Returns:
            Dict[str, Any]: النتائج المحسنة مع تحليل الفرصة
        """
        # التحليل التقليدي
        base_analysis = self._traditional_analysis(data)
        
        # تحليل الفرصة المتقدم
        opportunity_result = self.opportunity_engine.analyze(symbol, data)
        
        # دمج النتائج
        return {
            **base_analysis,
            'opportunity': opportunity_result,
            'ai_confidence': opportunity_result.confidence,
            'ai_score': opportunity_result.opportunity_score,
            'recommendation': self._get_recommendation(opportunity_result),
        }
    
    def _traditional_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """التحليل التقليدي (مستمر)"""
        # محاكاة - سيتم استبدالها بالتحليل الفعلي
        return {
            'technical_score': 0.78,
            'fundamental_score': 0.65,
            'sentiment_score': 0.72,
        }
    
    def _get_recommendation(self, result) -> str:
        """الحصول على توصية بناءً على تحليل الفرصة"""
        score = result.opportunity_score
        
        if score >= 75:
            return "قوي"
        elif score >= 60:
            return "إيجابي"
        elif score >= 40:
            return "محايد"
        else:
            return "تجنب"
