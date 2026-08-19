"""Advanced, data-only opportunity signals built from the latest scan snapshot.

No extra Yahoo requests are made here. The functions operate on an existing
DataFrame so they are safe to use across Streamlit pages.
"""
from __future__ import annotations

import pandas as pd


def _num(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def enrich_advanced_signals(frame: pd.DataFrame) -> pd.DataFrame:
    """Add Squeeze, Volume Anomaly, Relative Strength and Breakout Retest signals."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return frame.copy()

    out = frame.copy()
    rvol = _num(out, "relative_volume", 1.0)
    momentum = _num(out, "momentum_score", 0.0)
    liquidity = _num(out, "liquidity_score", 0.0)
    confirmation = _num(out, "confirmation_score", 0.0)
    breakout = _num(out, "breakout_probability", 0.0)
    trend = _num(out, "trend_score", 0.0)
    change = _num(out, "change_pct", 0.0)

    # Squeeze proxy: low/normal volume followed by strong momentum/breakout.
    squeeze = ((rvol <= 1.15) & (momentum >= 65) & (breakout >= 60)).astype(int)
    volume_anomaly = ((rvol >= 2.0) | ((rvol >= 1.5) & (change.abs() >= 3))).astype(int)
    relative_strength = ((momentum * 0.45 + trend * 0.35 + confirmation * 0.20) >= 72).astype(int)
    breakout_retest = ((breakout >= 70) & (confirmation >= 60) & (rvol >= 1.25) & (momentum >= 65)).astype(int)

    out["squeeze_signal"] = squeeze
    out["volume_anomaly_signal"] = volume_anomaly
    out["relative_strength_signal"] = relative_strength
    out["breakout_retest_signal"] = breakout_retest

    signal_count = squeeze + volume_anomaly + relative_strength + breakout_retest
    out["advanced_signal_count"] = signal_count
    out["advanced_signal_score"] = (signal_count / 4.0 * 100.0).round(1)

    def label(row: pd.Series) -> str:
        names = []
        if row["squeeze_signal"]:
            names.append("Squeeze")
        if row["volume_anomaly_signal"]:
            names.append("Volume Anomaly")
        if row["relative_strength_signal"]:
            names.append("Relative Strength")
        if row["breakout_retest_signal"]:
            names.append("Breakout Retest")
        return " • ".join(names) if names else "لا توجد إشارة متقدمة"

    out["advanced_signals"] = out.apply(label, axis=1)

    # Small, bounded bonus: advanced signals influence ranking without overpowering
    # the canonical Opportunity Score already produced by the ranker.
    base = _num(out, "opportunity_score", 0.0)
    out["enhanced_opportunity_score"] = (base * 0.85 + out["advanced_signal_score"] * 0.15).clip(0, 100).round(1)
    return out
