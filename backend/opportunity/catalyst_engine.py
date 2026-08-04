"""
محرك تحليل المحفزات
"""

from typing import Dict, Any, List, Tuple
from .models import Catalysts


class CatalystEngine:
    """محرك تحليل المحفزات"""
    
    def __init__(self):
        self.catalyst_thresholds = {
            'technical': {
                'bollinger_squeeze': 0.3,
                'atr_compression': 0.4,
                'volume_spike': 1.8,
                'resistance_break': 1.02,
                'support_hold': 0.98,
                'pattern_bullish': 0.7,
            },
            'fundamental': {
                'earnings_beat': 0.05,
                'revenue_growth': 0.15,
                'profit_margin': 0.20,
                'debt_decrease': 0.10,
            },
            'sentiment': {
                'news_positive': 0.6,
                'social_mentions': 0.5,
                'analyst_upgrade': 0.7,
            },
            'institutional': {
                'smart_money_flow': 0.6,
                'institutional_ownership': 0.7,
                'insider_buying': 0.5,
            },
            'macro': {
                'sector_strength': 0.6,
                'market_regime_bullish': 0.7,
                'interest_rates_favorable': 0.5,
            }
        }
    
    def analyze_catalysts(self, data: Dict[str, Any]) -> Catalysts:
        """تحليل جميع المحفزات المتاحة"""
        catalysts = Catalysts()
        
        # المحفزات الفنية
        catalysts.technical = self._detect_technical_catalysts(data)
        
        # المحفزات الأساسية
        catalysts.fundamental = self._detect_fundamental_catalysts(data)
        
        # محفزات المشاعر
        catalysts.sentiment = self._detect_sentiment_catalysts(data)
        
        # المحفزات المؤسسية
        catalysts.institutional = self._detect_institutional_catalysts(data)
        
        # المحفزات الكلية
        catalysts.macro = self._detect_macro_catalysts(data)
        
        return catalysts
    
    def _detect_technical_catalysts(self, data: Dict[str, Any]) -> List[str]:
        """كشف المحفزات الفنية"""
        catalysts = []
        
        if data.get('bollinger_width', 1) < 0.3:
            catalysts.append("📊 تضيق نطاق بولينجر - استعداد للانفجار")
        
        if data.get('atr_ratio', 1) < 0.4:
            catalysts.append("📉 انكماش ATR - ضغط التقلبات")
        
        if data.get('volume_spike', 1) > 1.8:
            catalysts.append("📈 قفزة حجمية - اهتمام متزايد")
        
        if data.get('resistance_break', 1) > 1.02:
            catalysts.append("🚀 كسر المقاومة الرئيسية")
        
        if data.get('pattern_score', 0) > 0.7:
            catalysts.append("🎯 نموذج فني صاعد (Bull Flag / Cup & Handle)")
        
        if data.get('support_hold', 1) > 0.98:
            catalysts.append("🛡️ تماسك فوق الدعم الرئيسي")
        
        return catalysts
    
    def _detect_fundamental_catalysts(self, data: Dict[str, Any]) -> List[str]:
        """كشف المحفزات الأساسية"""
        catalysts = []
        
        eps_beat = data.get('eps_beat', 0)
        if eps_beat > 0.05:
            catalysts.append(f"💵 أرباح تفوق التوقعات بنسبة {eps_beat*100:.1f}%")
        
        if data.get('revenue_growth', 0) > 0.15:
            catalysts.append(f"📊 نمو الإيرادات {data['revenue_growth']*100:.1f}%")
        
        if data.get('profit_margin', 0) > 0.20:
            catalysts.append("💰 هوامش ربح مرتفعة")
        
        if data.get('debt_decrease', 0) > 0.10:
            catalysts.append("📉 انخفاض الدين بنسبة ملحوظة")
        
        return catalysts
    
    def _detect_sentiment_catalysts(self, data: Dict[str, Any]) -> List[str]:
        """كشف محفزات المشاعر"""
        catalysts = []
        
        if data.get('news_sentiment', 0) > 0.6:
            catalysts.append("📰 أخبار إيجابية قوية")
        
        if data.get('social_score', 0) > 0.5:
            catalysts.append("💬 ضجة إيجابية على وسائل التواصل")
        
        if data.get('analyst_rating', 0) > 0.7:
            catalysts.append("⭐ رفع التوصية من المحللين")
        
        return catalysts
    
    def _detect_institutional_catalysts(self, data: Dict[str, Any]) -> List[str]:
        """كشف المحفزات المؤسسية"""
        catalysts = []
        
        if data.get('smart_money_flow', 0) > 0.6:
            catalysts.append("🏦 تدفقات مؤسسية إيجابية (Smart Money)")
        
        if data.get('institutional_ownership', 0) > 0.7:
            catalysts.append("📈 ملكية مؤسسية عالية")
        
        if data.get('insider_buying', 0) > 0.5:
            catalysts.append("👔 شراء من قبل المدراء التنفيذيين")
        
        return catalysts
    
    def _detect_macro_catalysts(self, data: Dict[str, Any]) -> List[str]:
        """كشف المحفزات الكلية"""
        catalysts = []
        
        if data.get('sector_strength', 0) > 0.6:
            catalysts.append("🏭 القطاع أقوى من السوق")
        
        if data.get('market_regime', 0) > 0.7:
            catalysts.append("🌍 ظروف السوق داعمة للصعود")
        
        if data.get('interest_rates', 0) > 0.5:
            catalysts.append("💰 بيئة أسعار فائدة مواتية")
        
        return catalysts
    
    def get_catalyst_summary(self, catalysts: Catalysts) -> Dict[str, Any]:
        """الحصول على ملخص المحفزات"""
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
                catalysts.technical +
                catalysts.fundamental +
                catalysts.sentiment +
                catalysts.institutional +
                catalysts.macro
            )
        }
