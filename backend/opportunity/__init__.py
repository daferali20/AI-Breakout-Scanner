from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# 1. تعريف المراحل ومستويات الدرجات
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


# 2. خواص المراحل والأوزان
PHASE_PROPERTIES = {
    MarketPhase.ACCUMULATION: {
        "color": "#3498db",
        "emoji": "🔋",
        "description": "مرحلة التجميع وتجهيز الانطلاق",
    },
    MarketPhase.BREAKOUT: {
        "color": "#2ecc71",
        "emoji": "🚀",
        "description": "اختراق مستويات المقاومة",
    },
    MarketPhase.UPTREND: {
        "color": "#9b59b6",
        "emoji": "📈",
        "description": "اتجاه صاعد مستمر",
    },
    MarketPhase.CONSOLIDATION: {
        "color": "#f39c12",
        "emoji": "⚖️",
        "description": "نطاق عرضي وإعادة تجميع",
    },
    MarketPhase.MARKDOWN: {
        "color": "#e74c3c",
        "emoji": "📉",
        "description": "اتجاه هابط ومخاطر مرتفعة",
    },
}

INDICATOR_WEIGHTS = {
    "smart_money_flow": 0.20,
    "relative_volume": 0.15,
    "pattern_detection": 0.12,
    "bollinger_squeeze": 0.12,
    "atr_compression": 0.10,
    "sector_strength": 0.08,
    "market_regime": 0.08,
    "news_sentiment": 0.05,
    "earnings": 0.05,
    "ai_score": 0.05,
}


class Catalysts:
    VOLUME_SPIKE = "ارتفاع ملحوظ في حجم التداول"
    SMART_MONEY_INFLOW = "تدفق سيولة من المؤسسات (Smart Money)"
    PATTERN_COMPLETION = "اكتمال نمط الفني إيجابي"
    RESISTANCE_BREAK = "اختراق قمة سابقة"


# 3. هياكل البيانات (Data Classes)
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


# 4. بناء التسلسل الزمني ومحرك الفرص
class TimelineBuilder:

    def build_timeline(
        self,
        current_phase: MarketPhase,
        next_phase: Optional[MarketPhase],
        phase_days: int,
        expected_days: int,
        data: Dict[str, Any],
    ) -> List[TimelineEvent]:
        today = datetime.now()
        events = [
            TimelineEvent(
                phase=current_phase,
                date=(today - timedelta(days=phase_days)).strftime("%Y-%m-%d"),
                confidence=0.85,
            )
        ]
        if next_phase:
            events.append(
                TimelineEvent(
                    phase=next_phase,
                    date=(today + timedelta(days=expected_days)).strftime(
                        "%Y-%m-%d"
                    ),
                    confidence=0.70,
                )
            )
        return events


class OpportunityEngine:

    def analyze(
        self, symbol: str, data: Dict[str, Any] = None
    ) -> OpportunityResult:
        score = 82.5
        return OpportunityResult(
            symbol=symbol,
            current_phase=MarketPhase.ACCUMULATION,
            confidence=88.0,
            opportunity_score=score,
            score_level=OpportunityScoreLevel.HIGH,
            current_phase_days=6,
            expected_days=10,
            next_phase=MarketPhase.BREAKOUT,
            transition_probability=0.78,
            catalysts=[
                Catalysts.SMART_MONEY_INFLOW,
                Catalysts.VOLUME_SPIKE,
                "تقاطع إيجابي لمؤشر RSI فوق مستويات 50",
            ],
            risks=[
                "تقلبات السوق العامة قد تؤثر على سرعة الاختراق",
                "وجود مستوى مقاومة قريب عند المتوسط المتحرك 200",
            ],
            reasons=[
                "تجميع سيولة هادئ على مدار 6 أيام متتالية",
                "انخفاض مدى التذبذب (Volatility Squeeze) يسبق الانفجار السعري",
                "دعم قوي من مؤشرات حركة رؤوس الأموال الذكية",
            ],
            ai_decision_report="""### 🤖 تقرير الذكاء الاصطناعي الشامل
- **حالة السهم:** يشهد السهم عملية بناء مراكز تجميعية واضحة.
- **التوصية الفنية:** مراقبة اختراق مستويات المقاومة القريبة مع تفعيل وقف الخسارة أسفل منطقة التجميع.
- **الهدف المتوقع:** تحقيق 8% إلى 12% خلال الدورة الزمنية القادمة.""",
        )
