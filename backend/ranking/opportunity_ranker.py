"""Unified opportunity ranking engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

# Balanced score: setup + momentum + liquidity + breakout probability + trend.
# Risk is a separate penalty so an attractive but dangerous setup cannot dominate.
POSITIVE_WEIGHTS = {
    "setup_score": 0.25,
    "momentum_score": 0.20,
    "liquidity_score": 0.20,
    "breakout_probability": 0.20,
    "trend_score": 0.10,
}
RISK_PENALTY_MAX = 5.0


def _score(value: Any) -> float:
    try:
        return float(max(0.0, min(100.0, float(value))))
    except (TypeError, ValueError):
        return 0.0


def _reason(row: pd.Series) -> str:
    reasons = []
    if _score(row.get("breakout_probability")) >= 75:
        reasons.append("احتمال اختراق مرتفع")
    if _score(row.get("confirmation_score")) >= 75:
        reasons.append("تأكيد قوي")
    if _score(row.get("liquidity_score")) >= 70:
        reasons.append("سيولة جيدة")
    if _score(row.get("momentum_score")) >= 70:
        reasons.append("زخم قوي")
    if _score(row.get("trend_score")) >= 70:
        reasons.append("اتجاه صاعد مستقر")
    try:
        rv = float(row.get("relative_volume", 0))
        if rv >= 1.5:
            reasons.append(f"حجم نسبي {rv:.1f}x")
    except (TypeError, ValueError):
        pass
    risk = _score(row.get("false_breakout_risk"))
    if risk >= 55:
        reasons.append("⚠️ خطر اختراق كاذب مرتفع")
    elif risk >= 35:
        reasons.append("مخاطرة متوسطة")
    return " • ".join(reasons[:5]) if reasons else "مرشح يحتاج إلى تأكيد إضافي"


def rank_opportunities(rows: list[dict[str, Any]] | pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Return opportunities ranked on a consistent 0-100 scale."""
    frame = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty:
        return frame

    required = set(POSITIVE_WEIGHTS) | {"false_breakout_risk"}
    for column in required:
        if column not in frame.columns:
            frame[column] = 0.0
        frame[column] = frame[column].map(_score)

    # Confirmation is a quality gate, not a dominant score component.
    if "confirmation_score" not in frame.columns:
        frame["confirmation_score"] = 0.0
    frame["confirmation_score"] = frame["confirmation_score"].map(_score)

    positive_score = sum(frame[column] * weight for column, weight in POSITIVE_WEIGHTS.items())
    risk_penalty = (frame["false_breakout_risk"] / 100.0) * RISK_PENALTY_MAX
    confirmation_bonus = ((frame["confirmation_score"] - 50.0).clip(lower=0) / 50.0) * 3.0
    frame["opportunity_score"] = (positive_score - risk_penalty + confirmation_bonus).clip(0, 100).round(2)

    # Confidence reflects both opportunity quality and confirmation.
    frame["confidence_score"] = (
        frame["opportunity_score"] * 0.70 + frame["confirmation_score"] * 0.30
    ).round(1)

    frame["rank"] = frame["opportunity_score"].rank(method="first", ascending=False).astype(int)
    frame["signal_quality"] = pd.cut(
        frame["opportunity_score"],
        bins=[-1, 50, 65, 80, 101],
        labels=["Weak", "Watch", "Strong", "Elite"],
    ).astype(str)
    frame["signal_class"] = frame["signal_quality"].map({
        "Elite": "🔥 فرصة قوية",
        "Strong": "🟢 فرصة جيدة",
        "Watch": "🔵 مراقبة",
        "Weak": "🟡 ضعيفة",
    }).fillna("🟡 ضعيفة")

    frame["opportunity_reason"] = frame.apply(_reason, axis=1)

    # A strong opportunity should also have confirmation; avoid presenting
    # high-score but weakly confirmed setups as top picks.
    frame["trade_quality"] = frame.apply(
        lambda r: "جاهزة للمراقبة" if r["opportunity_score"] >= 75 and r["confirmation_score"] >= 65
        else "تحتاج تأكيد" if r["opportunity_score"] >= 60
        else "مبكرة",
        axis=1,
    )

    sort_columns = ["opportunity_score", "confidence_score", "breakout_probability"]
    if "relative_volume" in frame.columns:
        sort_columns.append("relative_volume")

    return frame.sort_values(sort_columns, ascending=False).head(max(1, int(top_n))).reset_index(drop=True)
