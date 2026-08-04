"""
AI Scanner - ماسح ذكي باستخدام تحليل الفرص
"""

from typing import List, Dict, Any
import pandas as pd

from backend.opportunity import OpportunityEngine


class AIScanner:
    """ماسح الذكاء الاصطناعي المتقدم"""
    
    def __init__(self):
        self.opportunity_engine = OpportunityEngine()
    
    def scan(self, symbols: List[str], market_data: Dict[str, Any]) -> pd.DataFrame:
        """
        مسح قائمة من الأسهم وتحليل فرصها
        
        Returns:
            pd.DataFrame: النتائج مرتبة حسب درجة الفرصة
        """
        results = []
        
        for symbol in symbols:
            data = market_data.get(symbol, {})
            
            try:
                opportunity = self.opportunity_engine.analyze(symbol, data)
                
                results.append({
                    'symbol': symbol,
                    'phase': opportunity.current_phase.value,
                    'phase_days': opportunity.current_phase_days,
                    'confidence': opportunity.confidence,
                    'next_phase': opportunity.next_phase.value if opportunity.next_phase else None,
                    'transition_prob': opportunity.transition_probability,
                    'opportunity_score': opportunity.opportunity_score,
                    'score_level': opportunity.score_level.value,
                    'catalysts': len(opportunity.catalysts),
                    'risks': len(opportunity.risks),
                })
            except Exception as e:
                print(f"خطأ في تحليل {symbol}: {e}")
                continue
        
        # ترتيب حسب درجة الفرصة
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('opportunity_score', ascending=False)
        
        return df
