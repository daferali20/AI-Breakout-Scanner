"""Smart alert generation from the canonical scan snapshot."""
from __future__ import annotations

from typing import Any

import pandas as pd


def generate_alerts(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    alerts: list[dict[str, Any]] = []

    def num(row: pd.Series, key: str, default: float = 0.0) -> float:
        try:
            return float(row.get(key, default) or default)
        except (TypeError, ValueError):
            return default

    for _, row in frame.iterrows():
        symbol = str(row.get("symbol", "—"))
        score = num(row, "enhanced_opportunity_score", num(row, "opportunity_score"))
        rvol = num(row, "relative_volume", 1)
        momentum = num(row, "momentum_score")
        breakout = num(row, "breakout_probability")
        risk = num(row, "false_breakout_risk", 100)
        signals = str(row.get("advanced_signals", ""))

        if score >= 85 and risk <= 25:
            alerts.append({"symbol": symbol, "type": "ELITE", "priority": "HIGH", "message": "فرصة Elite بثقة جيدة ومخاطر اختراق كاذب منخفضة."})
        elif rvol >= 3 and momentum >= 80:
            alerts.append({"symbol": symbol, "type": "VOLUME", "priority": "HIGH", "message": "تدفق حجم استثنائي مع زخم قوي."})
        elif breakout >= 80 and risk <= 30:
            alerts.append({"symbol": symbol, "type": "BREAKOUT", "priority": "HIGH", "message": "احتمال اختراق مرتفع مع مخاطرة محدودة."})
        elif "Breakout Retest" in signals:
            alerts.append({"symbol": symbol, "type": "RETEST", "priority": "MEDIUM", "message": "إشارة إعادة اختبار للاختراق مع تأكيد جيد."})
        elif "Squeeze" in signals:
            alerts.append({"symbol": symbol, "type": "SQUEEZE", "priority": "MEDIUM", "message": "ضغط سعري قد يسبق حركة قوية."})

    priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(alerts, key=lambda x: priority.get(x["priority"], 9))
