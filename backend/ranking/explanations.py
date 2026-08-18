"""Human-readable explanations for opportunity ranking."""

from __future__ import annotations

from typing import Any


def explain_opportunity(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    probability = float(row.get("breakout_probability", 0) or 0)
    liquidity = float(row.get("liquidity_score", 0) or 0)
    momentum = float(row.get("momentum_score", 0) or 0)
    trend = float(row.get("trend_score", 0) or 0)
    risk = float(row.get("false_breakout_risk", 100) or 100)
    rvol = float(row.get("relative_volume", 0) or 0)

    if probability >= 80:
        reasons.append("High ML breakout probability")
    elif probability >= 65:
        reasons.append("Positive ML breakout probability")
    if liquidity >= 80:
        reasons.append("Strong liquidity")
    if rvol >= 2:
        reasons.append("High relative volume")
    if momentum >= 80:
        reasons.append("Strong momentum")
    if trend >= 80:
        reasons.append("Strong trend")
    if risk <= 20:
        reasons.append("Low false-breakout risk")
    elif risk >= 60:
        reasons.append("High false-breakout risk")
    return reasons or ["No dominant signal yet"]
