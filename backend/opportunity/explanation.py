"""
توليد شرح لقرارات المحرك
"""

from typing import Dict, Any, List
from .models import MarketPhase, PhaseMetrics, Catalysts, PHASE_PROPERTIES


class ExplanationGenerator:
    """مولد الشروحات التفصيلية"""
    
    def generate_reasons(self, phase_metrics: PhaseMetrics, 
                        catalysts: Catalysts, data: Dict[str, Any]) -> List[str]:
        """توليد أسباب التقييم"""
        reasons = []
        phase = phase_metrics.phase
        
        # أسباب متعلقة بالمرحلة
        phase_desc = PHASE_PROPERTIES.get(phase, {}).get('description', '')
        reasons.append(f"📊 المرحلة الحالية: {phase_desc}")
        
        # أسباب فنية
        if data.get('bollinger_width', 1) < 0.3:
            reasons.append(f"📉 انكماش نطاق بولينجر بنسبة {(1-data.get('bollinger_width', 1))*100:.1f}%")
        
        if data.get('atr_ratio', 1) < 0.4:
            reasons.append(f"📊 انخفاض ATR بنسبة {(1-data.get('atr_ratio', 1))*100:.1f}%")
        
        if data.get('volume_trend', 1) > 1.5:
            reasons.append(f"📈 ارتفاع متوسط الحجم النسبي إلى {data.get('volume_trend', 1):.1f}x")
        
        if data.get('pattern_score', 0) > 0.7:
            reasons.append("🎯 رصد نموذج فني صاعد (Bull Flag)")
        
        # أسباب المحفزات
        total_cats = catalysts.total_catalysts()
        if total_cats >= 5:
            reasons.append(f"🔍 وجود {total_cats} محفزات تدعم الفرصة")
        elif total_cats >= 3:
            reasons.append(f"🔍 وجود {total_cats} محفزات تدعم الفرصة")
        
        # أسباب متعلقة بالثقة
        if phase_metrics.confidence > 80:
            reasons.append(f"🎯 ثقة عالية ({phase_metrics.confidence:.1f}%) في التحليل")
        
        # أسباب الانتقال
        if phase_metrics.next_phase:
            reasons.append(f"➡️ احتمال انتقال للمرحلة التالية {phase_metrics.probability_next*100:.1f}%")
        
        return reasons
