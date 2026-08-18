"""Opportunity phase detection and scoring primitives."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class MarketPhase(Enum):
    ACCUMULATION = "accumulation"
    BREAKOUT = "breakout"
    UPTREND = "uptrend"
    CONSOLIDATION = "consolidation"
    MARKDOWN = "markdown"


class OpportunityScoreLevel(Enum):
    VERY_HIGH = "ممتازة جداً"
    HIGH = "مرتفعة"
    MEDIUM = "متوسطة"
    LOW = "منخفضة"


PHASE_PROPERTIES = {
    MarketPhase.ACCUMULATION: {"color": "#3498db", "emoji": "🔋", "description": "مرحلة التجميع وتجهيز الانطلاق"},
    MarketPhase.BREAKOUT: {"color": "#2ecc71", "emoji": "🚀", "description": "اختراق مستويات المقاومة"},
    MarketPhase.UPTREND: {"color": "#9b59b6", "emoji": "📈", "description": "اتجاه صاعد مستمر"},
    MarketPhase.CONSOLIDATION: {"color": "#f39c12", "emoji": "⚖️", "description": "نطاق عرضي وإعادة تجميع"},
    MarketPhase.MARKDOWN: {"color": "#e74c3c", "emoji": "📉", "description": "اتجاه هابط ومخاطر مرتفعة"},
}

INDICATOR_WEIGHTS = {
    "smart_money_flow": 0.20, "relative_volume": 0.15, "pattern_detection": 0.12,
    "bollinger_squeeze": 0.12, "atr_compression": 0.10, "sector_strength": 0.08,
    "market_regime": 0.08, "news_sentiment": 0.05, "earnings": 0.05, "ai_score": 0.05,
}


class Catalysts:
    VOLUME_SPIKE = "ارتفاع ملحوظ في حجم التداول"
    SMART_MONEY_INFLOW = "تدفق سيولة من المؤسسات (Smart Money)"
    PATTERN_COMPLETION = "اكتمال نمط الفني إيجابي"
    RESISTANCE_BREAK = "اختراق قمة سابقة"


@dataclass
class PhaseMetrics:
    phase: str
    days_in_phase: int
    confidence: float = 0.0


class PhaseDetector:
    """Classify the current market phase from normalized liquidity features."""

    def get_phase_metrics(self, data: Dict[str, Any], symbol: str = "") -> PhaseMetrics:
        rvol = self._num(data.get("relative_volume", 1.0), 1.0)
        price_change = self._num(data.get("price_change", 0.0), 0.0)
        smart_money = self._num(data.get("smart_money_score", 50.0), 50.0)
        compression = self._num(data.get("compression_level", 0.0), 0.0)
        resistance_break = self._num(data.get("resistance_break", 1.0), 1.0)
        trend = self._num(data.get("trend_strength", 0.5), 0.5)
        if resistance_break >= 1.0 and rvol >= 1.5 and price_change > 0:
            phase = MarketPhase.BREAKOUT.value
        elif trend >= 0.65 and price_change >= 0:
            phase = MarketPhase.UPTREND.value
        elif trend <= 0.35 and price_change < 0:
            phase = MarketPhase.MARKDOWN.value
        elif compression >= 0.55 and smart_money >= 55:
            phase = MarketPhase.ACCUMULATION.value
        else:
            phase = MarketPhase.CONSOLIDATION.value
        confidence = min(100.0, max(0.0, 50.0 + abs(trend - 0.5) * 100.0 + (rvol - 1.0) * 10.0))
        return PhaseMetrics(phase=phase, days_in_phase=5, confidence=confidence)

    @staticmethod
    def _num(value: Any, default: float) -> float:
        try:
            value = float(value)
            return value if value == value else default
        except (TypeError, ValueError):
            return default


@dataclass
class OpportunityResult:
    symbol: str
    current_phase: MarketPhase
    confidence: float
    opportunity_score: float
    score_level: OpportunityScoreLevel
    current_phase_days: int = 5
    expected_days: int = 14
    next_phase: Optional[MarketPhase] = MarketPhase.BREAKOUT
    transition_probability: float = 0.75
    catalysts: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    ai_decision_report: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TimelineEvent:
    phase: MarketPhase
    date: str
    confidence: float


class TimelineBuilder:
    def build_timeline(self, current_phase: MarketPhase, next_phase: Optional[MarketPhase], phase_days: int, expected_days: int, data: Dict[str, Any]) -> List[TimelineEvent]:
        today = datetime.now()
        events = [TimelineEvent(current_phase, (today - timedelta(days=phase_days)).strftime("%Y-%m-%d"), 0.85)]
        if next_phase:
            events.append(TimelineEvent(next_phase, (today + timedelta(days=expected_days)).strftime("%Y-%m-%d"), 0.70))
        return events


class OpportunityEngine:
    def analyze(self, symbol: str, data: Dict[str, Any] = None) -> OpportunityResult:
        return OpportunityResult(
            symbol=symbol, current_phase=MarketPhase.ACCUMULATION, confidence=88.0,
            opportunity_score=82.5, score_level=OpportunityScoreLevel.HIGH,
            current_phase_days=6, expected_days=10, next_phase=MarketPhase.BREAKOUT,
            transition_probability=0.78,
            catalysts=[Catalysts.SMART_MONEY_INFLOW, Catalysts.VOLUME_SPIKE],
            risks=["تقلبات السوق العامة قد تؤثر على سرعة الاختراق"],
            reasons=["تجميع سيولة", "انخفاض التذبذب", "دعم من حركة السيولة الذكية"],
            ai_decision_report="### 🤖 تقرير الذكاء الاصطناعي\nمراقبة الاختراق مع إدارة المخاطر.",
        )
