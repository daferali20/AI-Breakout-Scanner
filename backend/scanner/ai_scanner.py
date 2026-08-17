"""AI opportunity scanner combining phase analysis and breakout evidence."""

from typing import Any, Dict, List

import pandas as pd

from backend.opportunity import OpportunityEngine
from backend.scanner.breakout_scanner import BreakoutScanner


class AIScanner:
    """Rank symbols using phase analysis plus technical breakout evidence."""

    def __init__(self) -> None:
        self.opportunity_engine = OpportunityEngine()
        self.breakout_scanner = BreakoutScanner()

    def scan(self, symbols: List[str], market_data: Dict[str, Any]) -> pd.DataFrame:
        results = []
        for symbol in symbols:
            data = market_data.get(symbol, {})
            try:
                opportunity = self.opportunity_engine.analyze(symbol, data)
                breakout = data.get("breakout_result")
                ohlcv = data.get("ohlcv")
                if breakout is None and isinstance(ohlcv, pd.DataFrame):
                    breakout = self.breakout_scanner.scan_stock(symbol, ohlcv)
                breakout = breakout if isinstance(breakout, dict) else {}

                opportunity_score = float(opportunity.opportunity_score)
                breakout_score = float(breakout.get("score", data.get("breakout_score", 50)))
                combined = 0.60 * opportunity_score + 0.40 * breakout_score

                results.append({
                    "symbol": symbol.upper(),
                    "phase": opportunity.current_phase.value,
                    "phase_days": opportunity.current_phase_days,
                    "confidence": round(float(opportunity.confidence), 2),
                    "next_phase": opportunity.next_phase.value if opportunity.next_phase else None,
                    "transition_prob": round(float(opportunity.transition_probability), 4),
                    "opportunity_score": round(opportunity_score, 2),
                    "breakout_score": round(breakout_score, 2),
                    "combined_score": round(combined, 2),
                    "breakout_probability": breakout.get("breakout_probability"),
                    "false_breakout_risk": breakout.get("false_breakout_risk"),
                    "score_level": opportunity.score_level.value,
                    "catalysts": len(opportunity.catalysts),
                    "risks": len(opportunity.risks),
                })
            except Exception as exc:
                print(f"خطأ في تحليل {symbol}: {exc}")

        if not results:
            return pd.DataFrame()
        return pd.DataFrame(results).sort_values("combined_score", ascending=False).reset_index(drop=True)
