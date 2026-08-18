"""Performance report utilities for breakout backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_performance_report(returns: pd.Series, holding_days: pd.Series | None = None) -> dict[str, float]:
    r = pd.to_numeric(returns, errors="coerce").dropna()
    if r.empty:
        return {"signals": 0, "wins": 0, "losses": 0, "win_rate": 0.0, "avg_return": 0.0, "median_return": 0.0, "profit_factor": 0.0, "expectancy": 0.0, "max_drawdown": 0.0, "max_gain": 0.0, "max_loss": 0.0, "avg_holding_days": 0.0}
    equity = (1 + r).cumprod()
    drawdown = equity / equity.cummax() - 1
    gains = r[r > 0].sum()
    losses = -r[r < 0].sum()
    report = {
        "signals": float(len(r)),
        "wins": float((r > 0).sum()),
        "losses": float((r <= 0).sum()),
        "win_rate": float((r > 0).mean() * 100),
        "avg_return": float(r.mean() * 100),
        "median_return": float(r.median() * 100),
        "profit_factor": float(gains / losses) if losses > 0 else float("inf"),
        "expectancy": float(r.mean() * 100),
        "max_drawdown": float(drawdown.min() * 100),
        "max_gain": float(r.max() * 100),
        "max_loss": float(r.min() * 100),
        "avg_holding_days": float(pd.to_numeric(holding_days, errors="coerce").mean()) if holding_days is not None else 0.0,
    }
    return report


def calibration_table(probabilities: pd.Series, outcomes: pd.Series, bins: int = 10) -> pd.DataFrame:
    p = pd.to_numeric(probabilities, errors="coerce")
    y = pd.to_numeric(outcomes, errors="coerce")
    frame = pd.DataFrame({"probability": p, "outcome": y}).dropna()
    if frame.empty:
        return pd.DataFrame(columns=["bin", "samples", "predicted_probability", "actual_rate"])
    frame["bin"] = pd.cut(frame["probability"], bins=np.linspace(0, 100, bins + 1), include_lowest=True)
    grouped = frame.groupby("bin", observed=True)
    return grouped.agg(
        samples=("outcome", "size"),
        predicted_probability=("probability", "mean"),
        actual_rate=("outcome", "mean"),
    ).reset_index()
