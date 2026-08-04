"""
نماذج مراحل الفرصة الاستثمارية
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


class MarketPhase(str, Enum):
    """مراحل السوق"""
    ACCUMULATION = "accumulation"          # تجميع
    COMPRESSION = "compression"            # ضغط سيولة
    MOMENTUM = "momentum"                  # زخم
    BREAKOUT_READY = "breakout_ready"      # جاهزية اختراق
    BREAKOUT = "breakout"                  # اختراق فعلي
    TREND_CONTINUATION = "trend_continuation"  # استمرار الاتجاه
    DISTRIBUTION = "distribution"          # توزيع
    DECLINE = "decline"                    # هبوط


class OpportunityScoreLevel(str, Enum):
    """مستويات فرصة الاستثمار"""
    EXCELLENT = "excellent"    # 90-100%
    VERY_GOOD = "very_good"    # 75-89%
    GOOD = "good"              # 60-74%
    MODERATE = "moderate"      # 40-59%
    POOR = "poor"              # 0-39%


@dataclass
class PhaseMetrics:
    """مقاييس المرحلة"""
    phase: MarketPhase
    start_date: datetime
    days_in_phase: int
    confidence: float  # 0-100
    probability_next: float  # 0-100
    expected_days_to_next: Optional[int] = None
    next_phase: Optional[MarketPhase] = None
    indicators: Dict[str, Any] = field(default_factory=dict)
    catalyst_signals: List[str] = field(default_factory=list)


@dataclass
class OpportunityResult:
    """نتيجة تحليل الفرصة"""
    # المعلومات الأساسية
    symbol: str
    current_phase: MarketPhase
    current_phase_days: int
    confidence: float
    
    # الانتقال
    next_phase: Optional[MarketPhase]
    transition_probability: float
    expected_days: Optional[int]
    
    # التقييم
    opportunity_score: float
    score_level: OpportunityScoreLevel
    
    # الشرح
    reasons: List[str]
    catalysts: List[str]
    risks: List[str]
    
    # الخامات
    raw_metrics: PhaseMetrics
    ai_decision_report: str
    
    # الطوابع الزمنية
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TimelineEvent:
    """حدث في التسلسل الزمني"""
    phase: MarketPhase
    date: datetime
    confidence: float
    metrics: Dict[str, Any]
    days_until: Optional[int] = None


@dataclass
class Catalysts:
    """المحفزات"""
    technical: List[str] = field(default_factory=list)
    fundamental: List[str] = field(default_factory=list)
    sentiment: List[str] = field(default_factory=list)
    institutional: List[str] = field(default_factory=list)
    macro: List[str] = field(default_factory=list)
    
    def total_catalysts(self) -> int:
        return len(self.technical + self.fundamental + self.sentiment + 
                   self.institutional + self.macro)
    
    def is_strong(self) -> bool:
        return self.total_catalysts() >= 5


# تعريف أوزان المؤشرات
INDICATOR_WEIGHTS = {
    'smart_money': 0.20,
    'relative_volume': 0.15,
    'bollinger_squeeze': 0.12,
    'atr_compression': 0.10,
    'pattern_detection': 0.12,
    'sector_strength': 0.08,
    'market_regime': 0.08,
    'news_sentiment': 0.05,
    'earnings': 0.05,
    'ai_score': 0.05,
}

# تعريف المراحل وخصائصها
PHASE_PROPERTIES = {
    MarketPhase.ACCUMULATION: {
        'color': '#2ecc71',
        'emoji': '📈',
        'description': 'مرحلة التجميع - المؤسسات تشتري بهدوء',
        'avg_duration': 14,
        'next_phases': [MarketPhase.COMPRESSION, MarketPhase.MOMENTUM]
    },
    MarketPhase.COMPRESSION: {
        'color': '#f39c12',
        'emoji': '📊',
        'description': 'ضغط السيولة - استعداد للانفجار',
        'avg_duration': 10,
        'next_phases': [MarketPhase.BREAKOUT_READY, MarketPhase.BREAKOUT]
    },
    MarketPhase.MOMENTUM: {
        'color': '#3498db',
        'emoji': '⚡',
        'description': 'زخم قوي - حركة سعرية متسارعة',
        'avg_duration': 7,
        'next_phases': [MarketPhase.BREAKOUT, MarketPhase.TREND_CONTINUATION]
    },
    MarketPhase.BREAKOUT_READY: {
        'color': '#9b59b6',
        'emoji': '🎯',
        'description': 'جاهزية الاختراق - على وشك الانطلاق',
        'avg_duration': 3,
        'next_phases': [MarketPhase.BREAKOUT]
    },
    MarketPhase.BREAKOUT: {
        'color': '#e74c3c',
        'emoji': '🚀',
        'description': 'اختراق فعلي - انطلاق السعر',
        'avg_duration': 5,
        'next_phases': [MarketPhase.TREND_CONTINUATION, MarketPhase.DISTRIBUTION]
    },
    MarketPhase.TREND_CONTINUATION: {
        'color': '#1abc9c',
        'emoji': '📈',
        'description': 'استمرار الاتجاه - الزخم مستمر',
        'avg_duration': 12,
        'next_phases': [MarketPhase.DISTRIBUTION, MarketPhase.DECLINE]
    },
    MarketPhase.DISTRIBUTION: {
        'color': '#e67e22',
        'emoji': '📉',
        'description': 'توزيع - بداية خروج المؤسسات',
        'avg_duration': 10,
        'next_phases': [MarketPhase.DECLINE]
    },
    MarketPhase.DECLINE: {
        'color': '#c0392b',
        'emoji': '🔻',
        'description': 'هبوط - اتجاه هابط قوي',
        'avg_duration': 15,
        'next_phases': [MarketPhase.ACCUMULATION]
    },
}
