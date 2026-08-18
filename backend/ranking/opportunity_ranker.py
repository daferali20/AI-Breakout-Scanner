"""Unified ranking engine for breakout opportunities."""

from __future__ import annotations

from typing import Any

import pandas as pd


WEIGHTS = {
    "breakout_probability": 0.30,
    "setup_score": 0.20,
    "liquidity_score": 0.15,
    "momentum_score": 0.15,
    "trend_score": 0.10,
    "false_breakout_risk": -0.10,
}


def _score(value: Any) -> float:
    try:
        return float(max(0.0, min(100.0, float(value))))
    except (TypeError, ValueError):
        return 0.0


def rank_opportunities(rows: list[dict[str, Any]] | pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    frame = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty:
        return frame
    for column in WEIGHTS:
        if column not in frame.columns:
            frame[column] = 0.0
        frame[column] = frame[column].map(_score)
    frame["opportunity_score"] = sum(
        frame[column] * weight for column, weight in WEIGHTS.items()
    ).clip(0, 100).round(2)
    frame["rank"] = frame["opportunity_score"].rank(method="first", ascending=False).astype(int)
    frame["signal_quality"] = pd.cut(
        frame["opportunity_score"],
        bins=[-1, 55, 70, 85, 101],
        labels=["Weak", "Watch", "Strong", "Elite"],
    ).astype(str)
    return frame.sort_values(["opportunity_score", "breakout_probability"], ascending=False).head(top_n).reset_index(drop=True)
