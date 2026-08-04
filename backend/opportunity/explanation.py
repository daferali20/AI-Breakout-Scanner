from typing import Dict, Any, List
from .models import MarketPhase, PhaseMetrics, Catalysts, PHASE_PROPERTIES

class ExplanationGenerator:
    def generate_reasons(self, phase_metrics: PhaseMetrics, 
                        catalysts: Catalysts, data: Dict[str, Any]) -> List[str]:
        reasons = []
        phase = phase_metrics.phase
        phase_desc = PHASE_PROPERTIES.get(phase, {}).get('description', '')
        reasons.append(f"📊 المرحلة الحالية: {phase_desc}")
        if data.get('bollinger_width', 1) < 0.3:
            reasons.append(f"📉 انكماش نطاق بولينجر")
        if data.get('atr_ratio', 1) < 0.4:
            reasons.append(f"📊 انخفاض ATR")
        if data.get('volume_trend', 1) > 1.5:
            reasons.append(f"📈 ارتفاع متوسط الحجم النسبي")
        if data.get('pattern_score', 0) > 0.7:
            reasons.append("🎯 رصد نموذج فني صاعد")
        total_cats = catalysts.total_catalysts()
        if total_cats >= 5:
            reasons.append(f"🔍 وجود {total_cats} محفزات تدعم الفرصة")
        if phase_metrics.confidence > 80:
            reasons.append(f"🎯 ثقة عالية ({phase_metrics.confidence:.1f}%) في التحليل")
        if phase_metrics.next_phase:
            reasons.append(f"➡️ احتمال انتقال للمرحلة التالية {phase_metrics.probability_next*100:.1f}%")
        return reasons
