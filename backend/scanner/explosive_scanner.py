"""
Explosive Scanner - ماسح الاختراقات
"""

from typing import List, Dict, Any
import pandas as pd

from backend.opportunity import MarketPhase, OpportunityEngine


class ExplosiveScanner:
    """ماسح الاختراقات والانفجارات السعرية"""
    
    def __init__(self):
        self.opportunity_engine = OpportunityEngine()
    
    def scan_explosive(self, symbols: List[str], data: Dict[str, Any]) -> pd.DataFrame:
        """البحث عن أسهم في مراحل انفجارية"""
        results = []
        
        for symbol in symbols:
            try:
                opportunity = self.opportunity_engine.analyze(symbol, data.get(symbol, {}))
                
                # تركيز على مراحل الضغط والاختراق
                if opportunity.current_phase in [
                    MarketPhase.COMPRESSION,
                    MarketPhase.BREAKOUT_READY
                ]:
                    results.append({
                        'symbol': symbol,
                        'phase': opportunity.current_phase.value,
                        'days': opportunity.current_phase_days,
                        'confidence': opportunity.confidence,
                        'prob_breakout': opportunity.transition_probability,
                        'expected_days': opportunity.expected_days,
                        'score': opportunity.opportunity_score,
                        'catalysts': len(opportunity.catalysts),
                    })
            except Exception as e:
                print(f"خطأ في مسح {symbol}: {e}")
                continue
        
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values('score', ascending=False)
        
        return df
