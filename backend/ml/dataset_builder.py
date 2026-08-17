"""Build leakage-safe breakout datasets with forward outcome statistics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.analysis.breakout_features import extract_breakout_features


def build_breakout_dataset(
    df: pd.DataFrame,
    horizon: int = 10,
    target_return: float = 0.05,
    stop_return: float = -0.03,
) -> pd.DataFrame:
    """Create one row per historical bar using only information known at that bar."""
    frame = df.copy().reset_index(drop=True)
    rows: list[dict] = []
    for i in range(len(frame) - horizon):
        history = frame.iloc[: i + 1]
        features = extract_breakout_features(history)
        if not features:
            continue
        future = frame.iloc[i + 1 : i + horizon + 1]
        entry = float(frame.iloc[i]["Close"])
        highs = pd.to_numeric(future["High"], errors="coerce")
        lows = pd.to_numeric(future["Low"], errors="coerce")
        closes = pd.to_numeric(future["Close"], errors="coerce")
        max_gain = float(highs.max() / entry - 1) if entry else 0.0
        max_loss = float(lows.min() / entry - 1) if entry else 0.0
        forward_return = float(closes.iloc[-1] / entry - 1) if entry else 0.0
        label = int(max_gain >= target_return and max_loss > stop_return)
        rows.append({
            **features,
            "label": label,
            "forward_return": forward_return,
            "mfe": max_gain,
            "mae": max_loss,
            "holding_horizon": horizon,
        })
    return pd.DataFrame(rows)
