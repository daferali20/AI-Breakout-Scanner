"""Unified opportunity ranking engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

# User-facing model: technical/setup 25%, momentum 20%, liquidity 20%,
# breakout probability 20%, trend stability 10%. The remaining 5 points are
# reserved for a risk penalty so high-risk setups cannot dominate the list.
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


def rank_opportunities(
    rows: list[dict[str, Any]] | pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return opportunities ranked on a consistent 0-100 scale."""
    frame = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty:
        return frame

    required = set(POSITIVE_WEIGHTS) | {"false_breakout_risk"}
    for column in required:
        if column not in frame.columns:
            frame[column] = 0.0
        frame[column] = frame[column].map(_score)

    positive_score = sum(
        frame[column] * weight for column, weight in POSITIVE_WEIGHTS.items()
    )
    risk_penalty = (frame["false_breakout_risk"] / 100.0) * RISK_PENALTY_MAX
    frame["opportunity_score"] = (positive_score - risk_penalty).clip(0, 100).round(2)

    frame["rank"] = (
        frame["opportunity_score"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    frame["signal_quality"] = pd.cut(
        frame["opportunity_score"],
        bins=[-1, 50, 65, 80, 101],
        labels=["Weak", "Watch", "Strong", "Elite"],
    ).astype(str)
    frame["signal_class"] = frame["signal_quality"].map(
        {
            "Elite": "🔥 فرصة قوية",
            "Strong": "🟢 فرصة جيدة",
            "Watch": "🔵 مراقبة",
            "Weak": "🟡 ضعيفة",
        }
    ).fillna("🟡 ضعيفة")

    sort_columns = ["opportunity_score", "breakout_probability"]
    if "relative_volume" in frame.columns:
        sort_columns.append("relative_volume")

    return (
        frame.sort_values(sort_columns, ascending=False)
        .head(max(1, int(top_n)))
        .reset_index(drop=True)
    )
