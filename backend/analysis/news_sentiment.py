"""
تحليل مشاعر الأخبار - مع دمج المحفزات
"""

from typing import Dict, Any, List
from backend.opportunity import CatalystEngine


class NewsSentimentAnalyzer:
    """محلل مشاعر الأخبار"""
    
    def __init__(self):
        self.catalyst_engine = CatalystEngine()
    
    def analyze_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """تحليل مشاعر الأخبار مع ربطها بالمحفزات"""
        # تحليل المشاعر التقليدي
        sentiment_score = self._calculate_sentiment(news_data)
        
        # تحويل إلى تنسيق المحفزات
        catalyst_data = {
            'news_sentiment': sentiment_score,
            'social_score': self._social_mentions_analysis(news_data),
        }
        
        # استخدام محرك المحفزات
        catalysts = self.catalyst_engine.analyze_catalysts(catalyst_data)
        
        return {
            'sentiment_score': sentiment_score,
            'catalysts': catalysts,
            'catalyst_summary': self.catalyst_engine.get_catalyst_summary(catalysts),
        }
    
    def _calculate_sentiment(self, news_data: List[Dict]) -> float:
        """حساب درجة المشاعر"""
        # محاكاة - سيتم استبدالها بتحليل فعلي
        positive = sum(1 for n in news_data if n.get('sentiment', 0) > 0)
        negative = sum(1 for n in news_data if n.get('sentiment', 0) < 0)
        
        if positive + negative == 0:
            return 0.5
        
        return positive / (positive + negative)
    
    def _social_mentions_analysis(self, news_data: List[Dict]) -> float:
        """تحليل الإشارات على وسائل التواصل"""
        # محاكاة
        mentions = len(news_data)
        return min(1.0, mentions / 100)
