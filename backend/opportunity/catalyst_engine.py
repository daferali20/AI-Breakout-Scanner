from typing import Dict, Any, List
from .models import Catalysts

class CatalystEngine:
    def __init__(self):
        self.catalyst_thresholds = {
            'technical': {'bollinger_squeeze': 0.3, 'atr_compression': 0.4, 'volume_spike': 1.8, 'resistance_break': 1.02},
            'fundamental': {'earnings_beat': 0.05, 'revenue_growth': 0.15, 'profit_margin': 0.20},
            'sentiment': {'news_positive': 0.6, 'social_mentions': 0.5, 'analyst_upgrade': 0.7},
            'institutional': {'smart_money_flow': 0.6, 'institutional_ownership': 0.7},
            'macro': {'sector_strength': 0.6, 'market_regime_bullish': 0.7}
        }
    
    def analyze_catalysts(self, data: Dict[str, Any]) -> Catalysts:
        catalysts = Catalysts()
        catalysts.technical = self._detect_technical_catalysts(data)
        catalysts.fundamental = self._detect_fundamental_catalysts(data)
        catalysts.sentiment = self._detect_sentiment_catalysts(data)
        catalysts.institutional = self._detect_institutional_catalysts(data)
        catalysts.macro = self._detect_macro_catalysts(data)
        return catalysts
    
    def _detect_technical_catalysts(self, data: Dict[str, Any]) -> List[str]:
        catalysts = []
        if data.get('bollinger_width', 1) < 0.3:
            catalysts.append("📊 تضيق نطاق بولينجر")
        if data.get('atr_ratio', 1) < 0.4:
            catalysts.append("📉 انكماش ATR - ضغط التقلبات")
        if data.get('volume_spike', 1) > 1.8:
            catalysts.append("📈 قفزة حجمية - اهتمام متزايد")
        if data.get('resistance_break', 1) > 1.02:
            catalysts.append("🚀 كسر المقاومة الرئيسية")
        if data.get('pattern_score', 0) > 0.7:
            catalysts.append("🎯 نموذج فني صاعد")
        return catalysts
    
    def _detect_fundamental_catalysts(self, data: Dict[str, Any]) -> List[str]:
        catalysts = []
        if data.get('eps_beat', 0) > 0.05:
            catalysts.append(f"💵 أرباح تفوق التوقعات")
        if data.get('revenue_growth', 0) > 0.15:
            catalysts.append(f"📊 نمو الإيرادات")
        if data.get('profit_margin', 0) > 0.20:
            catalysts.append("💰 هوامش ربح مرتفعة")
        return catalysts
    
    def _detect_sentiment_catalysts(self, data: Dict[str, Any]) -> List[str]:
        catalysts = []
        if data.get('news_sentiment', 0) > 0.6:
            catalysts.append("📰 أخبار إيجابية قوية")
        if data.get('social_score', 0) > 0.5:
            catalysts.append("💬 ضجة إيجابية على وسائل التواصل")
        return catalysts
    
    def _detect_institutional_catalysts(self, data: Dict[str, Any]) -> List[str]:
        catalysts = []
        if data.get('smart_money_flow', 0) > 0.6:
            catalysts.append("🏦 تدفقات مؤسسية إيجابية")
        if data.get('institutional_ownership', 0) > 0.7:
            catalysts.append("📈 ملكية مؤسسية عالية")
        return catalysts
    
    def _detect_macro_catalysts(self, data: Dict[str, Any]) -> List[str]:
        catalysts = []
        if data.get('sector_strength', 0) > 0.6:
            catalysts.append("🏭 القطاع أقوى من السوق")
        if data.get('market_regime', 0) > 0.7:
            catalysts.append("🌍 ظروف السوق داعمة للصعود")
        return catalysts
    
    def get_catalyst_summary(self, catalysts: Catalysts) -> Dict[str, Any]:
        total = catalysts.total_catalysts()
        return {
            'total_catalysts': total,
            'is_strong': catalysts.is_strong(),
            'technical_count': len(catalysts.technical),
            'fundamental_count': len(catalysts.fundamental),
            'sentiment_count': len(catalysts.sentiment),
            'institutional_count': len(catalysts.institutional),
            'macro_count': len(catalysts.macro),
            'all_catalysts': (
                catalysts.technical + catalysts.fundamental +
                catalysts.sentiment + catalysts.institutional +
                catalysts.macro
            )
        }
