"""
كشف النماذج الفنية - مع دمج المحفزات
"""

from typing import Dict, Any, List
from backend.opportunity import CatalystEngine


class PatternDetector:
    """كاشف النماذج الفنية"""
    
    def __init__(self):
        self.catalyst_engine = CatalystEngine()
        self.patterns = ['Bull Flag', 'Cup & Handle', 'Ascending Triangle', 'Symmetrical Triangle']
    
    def detect_patterns(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """كشف النماذج الفنية مع تحليل المحفزات"""
        
        # كشف النماذج
        detected_patterns = self._scan_patterns(price_data)
        
        # حساب درجة النموذج
        pattern_score = self._calculate_pattern_score(detected_patterns, price_data)
        
        # استخدام محرك المحفزات
        catalyst_data = {
            'pattern_bullish': pattern_score,
        }
        catalysts = self.catalyst_engine.analyze_catalysts(catalyst_data)
        
        return {
            'patterns': detected_patterns,
            'pattern_score': pattern_score,
            'best_pattern': max(detected_patterns, key=detected_patterns.get) if detected_patterns else None,
            'catalysts': catalysts,
        }
    
    def _scan_patterns(self, data: Dict) -> Dict[str, float]:
        """مسح النماذج الفنية"""
        # محاكاة - سيعود بالدرجات الفعلية
        return {
            'Bull Flag': 0.82,
            'Cup & Handle': 0.45,
            'Ascending Triangle': 0.61,
        }
    
    def _calculate_pattern_score(self, patterns: Dict[str, float], data: Dict) -> float:
        """حساب درجة النموذج الإجمالية"""
        if not patterns:
            return 0.0
        
        return max(patterns.values())
