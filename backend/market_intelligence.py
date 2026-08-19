"""Unified market intelligence layer for opportunity lifecycle and risk/reward."""
from __future__ import annotations
from typing import Any
import pandas as pd


def _num(row: pd.Series, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def detect_market_regime(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"regime": "NEUTRAL", "score": 50.0, "label": "🟡 محايد"}
    score = pd.to_numeric(df.get("opportunity_score", 50), errors="coerce").fillna(50)
    momentum = pd.to_numeric(df.get("momentum_score", 50), errors="coerce").fillna(50)
    confidence = pd.to_numeric(df.get("confidence_score", 50), errors="coerce").fillna(50)
    composite = float((score.mean() * .45 + momentum.mean() * .35 + confidence.mean() * .20))
    if composite >= 70:
        return {"regime": "BULLISH", "score": round(composite, 1), "label": "🟢 صاعد"}
    if composite <= 40:
        return {"regime": "BEARISH", "score": round(composite, 1), "label": "🔴 هابط"}
    return {"regime": "NEUTRAL", "score": round(composite, 1), "label": "🟡 محايد"}


def lifecycle(row: pd.Series) -> str:
    score = _num(row, "enhanced_opportunity_score", _num(row, "opportunity_score", 0))
    breakout = _num(row, "breakout_probability")
    confirmation = _num(row, "confirmation_score")
    risk = _num(row, "false_breakout_risk", 50)
    momentum = _num(row, "momentum_score")
    if risk >= 65:
        return "WEAKENING"
    if breakout >= 80 and confirmation >= 75:
        return "CONFIRMED" if score >= 80 else "BREAKOUT"
    if momentum >= 70 and score >= 65:
        return "SETUP"
    return "WATCH"


def add_risk_reward(row: pd.Series) -> dict[str, Any]:
    price = _num(row, "price")
    if price <= 0:
        return {"entry": 0.0, "target": 0.0, "invalidation": 0.0, "risk_pct": 0.0, "reward_pct": 0.0, "rr": 0.0}
    high = _num(row, "52_week_high", price * 1.10)
    support = _num(row, "support", price * .96)
    entry = price
    invalidation = min(support, price * .97) if support > 0 else price * .97
    target = max(high, price * 1.08)
    risk_pct = max(0.1, (entry - invalidation) / entry * 100)
    reward_pct = max(0.1, (target - entry) / entry * 100)
    return {"entry": round(entry, 2), "target": round(target, 2), "invalidation": round(invalidation, 2), "risk_pct": round(risk_pct, 2), "reward_pct": round(reward_pct, 2), "rr": round(reward_pct / risk_pct, 2)}


def enrich_market_intelligence(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame(), detect_market_regime(pd.DataFrame())
    out = df.copy()
    regime = detect_market_regime(out)
    stages, entries, targets, invalidations, risks, rewards, ratios = [], [], [], [], [], [], []
    for _, row in out.iterrows():
        stages.append(lifecycle(row))
        rr = add_risk_reward(row)
        entries.append(rr["entry"]); targets.append(rr["target"]); invalidations.append(rr["invalidation"])
        risks.append(rr["risk_pct"]); rewards.append(rr["reward_pct"]); ratios.append(rr["rr"])
    out["opportunity_stage"] = stages
    out["entry_price"] = entries
    out["target_price"] = targets
    out["invalidation_price"] = invalidations
    out["risk_pct"] = risks
    out["reward_pct"] = rewards
    out["risk_reward"] = ratios
    base = pd.to_numeric(out.get("enhanced_opportunity_score", out.get("opportunity_score", 0)), errors="coerce").fillna(0)
    out["final_opportunity_score"] = (base + out["risk_reward"].clip(0, 3) * 3).clip(upper=100).round(1)
    return out.sort_values("final_opportunity_score", ascending=False).reset_index(drop=True), regime
