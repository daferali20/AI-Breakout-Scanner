"""
المحرك الرئيسي لتحليل الفرص الاستثمارية
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .models import (
    MarketPhase, OpportunityResult, OpportunityScoreLevel,
    PhaseMetrics, Catalysts, INDICATOR_WEIGHTS
)
from .phase_detector import PhaseDetector
from .transition_model import TransitionModel
from .catalyst_engine import CatalystEngine
from .confidence import ConfidenceCalculator
from .scoring import OpportunityScorer
from .explanation import ExplanationGenerator


class OpportunityEngine:
    """المحرك الرئيسي لتحليل الفرص"""
    
    def __init__(self):
        self.phase_detector = PhaseDetector()
        self.transition_model = TransitionModel()
        self.catalyst_engine = CatalystEngine()
        self.confidence_calculator = ConfidenceCalculator()
        self.scorer = OpportunityScorer()
        self.explanation_generator = ExplanationGenerator()
    
    def analyze(self, symbol: str, data: Dict[str, Any]) -> OpportunityResult:
        """
        تحليل فرصة السهم
        
        Args:
            symbol: رمز السهم
            data: بيانات السهم المحللة
        
        Returns:
            OpportunityResult: نتيجة التحليل الكاملة
        """
        # 1. تحديد المرحلة الحالية
        phase_metrics = self.phase_detector.get_phase_metrics(data, symbol)
        
        # 2. توقع المرحلة التالية
        next_phase, transition_prob, expected_days = self.transition_model.predict_next_phase(
            phase_metrics.phase, data
        )
        phase_metrics.next_phase = next_phase
        phase_metrics.probability_next = transition_prob
        phase_metrics.expected_days_to_next = expected_days
        
        # 3. تحليل المحفزات
        catalysts = self.catalyst_engine.analyze_catalysts(data)
        catalyst_summary = self.catalyst_engine.get_catalyst_summary(catalysts)
        
        # 4. حساب الثقة
        confidence = self.confidence_calculator.calculate(
            phase_metrics, data, catalyst_summary
        )
        phase_metrics.confidence = confidence
        
        # 5. حساب درجة الفرصة
        opportunity_score = self.scorer.calculate_score(
            phase_metrics, catalyst_summary, data
        )
        
        # 6. تحديد مستوى الفرصة
        score_level = self._get_score_level(opportunity_score)
        
        # 7. توليد الأسباب والمخاطر
        reasons = self.explanation_generator.generate_reasons(
            phase_metrics, catalysts, data
        )
        
        risks = self._identify_risks(phase_metrics, data)
        
        # 8. توليد تقرير AI
        ai_report = self._generate_ai_report(
            symbol, phase_metrics, catalysts, 
            opportunity_score, score_level
        )
        
        # 9. بناء النتيجة النهائية
        return OpportunityResult(
            symbol=symbol,
            current_phase=phase_metrics.phase,
            current_phase_days=phase_metrics.days_in_phase,
            confidence=confidence,
            next_phase=next_phase,
            transition_probability=transition_prob,
            expected_days=expected_days,
            opportunity_score=opportunity_score,
            score_level=score_level,
            reasons=reasons,
            catalysts=catalyst_summary['all_catalysts'],
            risks=risks,
            raw_metrics=phase_metrics,
            ai_decision_report=ai_report,
            analysis_timestamp=datetime.now()
        )
    
    def _get_score_level(self, score: float) -> OpportunityScoreLevel:
        """تحديد مستوى الفرصة"""
        if score >= 90:
            return OpportunityScoreLevel.EXCELLENT
        elif score >= 75:
            return OpportunityScoreLevel.VERY_GOOD
        elif score >= 60:
            return OpportunityScoreLevel.GOOD
        elif score >= 40:
            return OpportunityScoreLevel.MODERATE
        else:
            return OpportunityScoreLevel.POOR
    
    def _identify_risks(self, phase_metrics: PhaseMetrics, data: Dict[str, Any]) -> List[str]:
        """تحديد المخاطر المحتملة"""
        risks = []
        
        phase = phase_metrics.phase
        
        # مخاطر عامة
        if data.get('volatility', 0.5) > 0.7:
            risks.append("⚠️ تقلبات عالية قد تؤدي إلى إشارات خاطئة")
        
        if data.get('volume_trend', 1) < 0.6:
            risks.append("📉 ضعف الحجم قد يؤخر الاختراق")
        
        if data.get('market_regime', 0.5) < 0.3:
            risks.append("🌍 ظروف السوق غير مواتية حالياً")
        
        # مخاطر خاصة بالمرحلة
        if phase == MarketPhase.COMPRESSION:
            risks.append("⏳ ضغط السيولة قد يستمر لفترة أطول من المتوقع")
            risks.append("📊 احتمال الاختراق للأسفل (فشل النموذج) ~13%")
        elif phase == MarketPhase.BREAKOUT_READY:
            risks.append("🎯 قد يكون الاختراق كاذباً (فخ صاعد)")
            risks.append("📉 احتمال الارتداد من المقاومة ~22%")
        elif phase == MarketPhase.MOMENTUM:
            risks.append("⚡ خطر تشبع الشراء (Overbought)")
            risks.append("📉 احتمال التصحيح خلال 3-5 أيام ~35%")
        
        return risks[:3]  # عرض أهم 3 مخاطر فقط
    
    def _generate_ai_report(self, symbol: str, phase_metrics: PhaseMetrics,
                           catalysts: Catalysts, score: float, 
                           score_level: OpportunityScoreLevel) -> str:
        """توليد تقرير AI شامل"""
        phase_emoji = {
            MarketPhase.ACCUMULATION: "📈",
            MarketPhase.COMPRESSION: "📊",
            MarketPhase.MOMENTUM: "⚡",
            MarketPhase.BREAKOUT_READY: "🎯",
            MarketPhase.BREAKOUT: "🚀",
            MarketPhase.TREND_CONTINUATION: "📈",
            MarketPhase.DISTRIBUTION: "📉",
            MarketPhase.DECLINE: "🔻",
        }.get(phase_metrics.phase, "📊")
        
        report = f"""
🤖 **تقرير AI - تحليل الفرصة**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 **السهم:** {symbol}
⏰ **وقت التحليل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{phase_emoji} **المرحلة الحالية:** {phase_metrics.phase.value}
📅 **المدة:** {phase_metrics.days_in_phase} يوماً
🎯 **الثقة:** {phase_metrics.confidence:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

➡️ **المرحلة التالية:** {phase_metrics.next_phase.value if phase_metrics.next_phase else 'غير محدد'}
📊 **احتمال الانتقال:** {phase_metrics.probability_next*100:.1f}%
⏳ **الأيام المتوقعة:** {phase_metrics.expected_days_to_next or 'غير محدد'} يوماً

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **درجة الفرصة:** {score:.1f}% ({score_level.value})

{self._get_score_bar(score)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 **المحفزات الرئيسية ({catalysts.total_catalysts()})**

{self._format_catalysts(catalysts)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **المخاطر المحتملة**

{self._format_risks(self._identify_risks(phase_metrics, {}))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
