from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MarketPhase(str, Enum):
    ACCUMULATION = "accumulation"
    COMPRESSION = "compression"
    MOMENTUM = "momentum"
    BREAKOUT_READY = "breakout_ready"
    BREAKOUT = "breakout"
    TREND_CONTINUATION = "trend_continuation"
    DISTRIBUTION = "distribution"
    DECLINE = "decline"

class OpportunityScoreLevel(str, Enum):
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"

@dataclass
class PhaseMetrics:
    phase: MarketPhase
    start_date: datetime
    days_in_phase: int
    confidence: float
    probability_next: float
    expected_days_to_next: Optional[int] = None
    next_phase: Optional[MarketPhase] = None
    indicators: Dict[str, Any] = field(default_factory=dict)
    catalyst_signals: List[str] = field(default_factory=list)

@dataclass
class OpportunityResult:
    symbol: str
    current_phase: MarketPhase
    current_phase_days: int
    confidence: float
    next_phase: Optional[MarketPhase]
    transition_probability: float
    expected_days: Optional[int]
    opportunity_score: float
    score_level: OpportunityScoreLevel
    reasons: List[str]
    catalysts: List[str]
    risks: List[str]
    raw_metrics: PhaseMetrics
    ai_decision_report: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TimelineEvent:
    phase: MarketPhase
    date: datetime
    confidence: float
    metrics: Dict[str, Any]
    days_until: Optional[int] = None

@dataclass
class Catalysts:
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
