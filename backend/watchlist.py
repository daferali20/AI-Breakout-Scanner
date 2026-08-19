"""Smart watchlist derived from the canonical ranking snapshot."""
from __future__ import annotations

import pandas as pd


def build_smart_watchlist(frame: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return pd.DataFrame()
    out = frame.copy()
    for col in ["enhanced_opportunity_score", "opportunity_score", "confidence_score", "relative_volume", "momentum_score", "false_breakout_risk", "advanced_signal_count"]:
        if col not in out:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    # Prefer quality + confirmation, then unusual activity, while penalizing risk.
    out["watchlist_score"] = (
        out["enhanced_opportunity_score"] * 0.40
        + out["confidence_score"] * 0.20
        + out["momentum_score"] * 0.15
        + out["relative_volume"].clip(0, 4) / 4 * 100 * 0.10
        + out["advanced_signal_count"] / 4 * 100 * 0.10
        + (100 - out["false_breakout_risk"].clip(0, 100)) * 0.05
    ).clip(0, 100).round(1)

    out["watch_status"] = "WATCH"
    out.loc[(out["watchlist_score"] >= 80) & (out["false_breakout_risk"] <= 30), "watch_status"] = "PRIORITY"
    out.loc[(out["watchlist_score"] >= 90) & (out["relative_volume"] >= 2), "watch_status"] = "HOT"

    return out.sort_values(["watchlist_score", "enhanced_opportunity_score"], ascending=False).head(limit).reset_index(drop=True)
