"""Shared in-process result store for the dashboard and scanner pages."""

from __future__ import annotations

from threading import RLock
from typing import Any

import pandas as pd

_LOCK = RLock()
_STORE: dict[str, Any] = {
    "scan_results": pd.DataFrame(),
    "scan_results_all": pd.DataFrame(),
    "ranked_results": pd.DataFrame(),
    "top_opportunities": pd.DataFrame(),
    "smart_watchlist": pd.DataFrame(),
    "alerts": [],
    "scan_errors": pd.DataFrame(),
    "scan_symbols_count": 0,
    "scan_success_count": 0,
    "last_scan_time": None,
    "scan_universe_source": "لم يتم إجراء مسح بعد",
    "market_regime": None,
    "opportunity_summary": {},
}


def _build_ranked(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    try:
        from backend.ranking.opportunity_ranker import rank_opportunities
        ranked = rank_opportunities(frame, top_n=max(len(frame), 1))
    except Exception:
        ranked = frame.copy()
    try:
        from backend.analysis.advanced_signals import enrich_advanced_signals
        ranked = enrich_advanced_signals(ranked)
    except Exception:
        pass
    return ranked


def _summary(ranked: pd.DataFrame) -> dict[str, Any]:
    if ranked.empty:
        return {"count": 0, "strong": 0, "elite": 0, "high_confidence": 0, "exceptional_flow": 0, "average_score": 0.0, "advanced_signals": 0}
    score = pd.to_numeric(ranked.get("enhanced_opportunity_score", ranked.get("opportunity_score", 0)), errors="coerce").fillna(0)
    confidence = pd.to_numeric(ranked.get("confidence_score", 0), errors="coerce").fillna(0)
    rvol = pd.to_numeric(ranked.get("relative_volume", 0), errors="coerce").fillna(0)
    momentum = pd.to_numeric(ranked.get("momentum_score", 0), errors="coerce").fillna(0)
    liquidity = pd.to_numeric(ranked.get("liquidity_score", 0), errors="coerce").fillna(0)
    advanced = pd.to_numeric(ranked.get("advanced_signal_count", 0), errors="coerce").fillna(0)
    return {
        "count": int(len(ranked)),
        "strong": int((score >= 65).sum()),
        "elite": int((score >= 80).sum()),
        "high_confidence": int((confidence >= 80).sum()),
        "exceptional_flow": int(((rvol >= 3) & (momentum >= 80) & (liquidity >= 75)).sum()),
        "average_score": round(float(score.mean()), 1),
        "advanced_signals": int((advanced > 0).sum()),
    }


def save_scan(**values: Any) -> None:
    """Save one canonical snapshot used by all UI pages and intelligence tools."""
    with _LOCK:
        for key, value in values.items():
            _STORE[key] = value.copy() if isinstance(value, pd.DataFrame) else value

        all_results = _STORE.get("scan_results_all", pd.DataFrame())
        if not isinstance(all_results, pd.DataFrame) or all_results.empty:
            return

        ranked = _build_ranked(all_results)
        _STORE["ranked_results"] = ranked.copy()
        _STORE["top_opportunities"] = ranked.head(10).copy()
        _STORE["scan_results"] = ranked.head(10).copy()

        try:
            from backend.watchlist import build_smart_watchlist
            _STORE["smart_watchlist"] = build_smart_watchlist(ranked, limit=25)
        except Exception:
            _STORE["smart_watchlist"] = ranked.head(25).copy()

        try:
            from backend.alerts import generate_alerts
            _STORE["alerts"] = generate_alerts(ranked)
        except Exception:
            _STORE["alerts"] = []

        _STORE["opportunity_summary"] = _summary(ranked)


def get_scan() -> dict[str, Any]:
    """Return a defensive copy of the latest unified scan snapshot."""
    with _LOCK:
        snapshot = dict(_STORE)
        for key in (
            "scan_results",
            "scan_results_all",
            "ranked_results",
            "top_opportunities",
            "smart_watchlist",
            "scan_errors",
        ):
            if isinstance(snapshot[key], pd.DataFrame):
                snapshot[key] = snapshot[key].copy()
        if isinstance(snapshot.get("alerts"), list):
            snapshot["alerts"] = list(snapshot["alerts"])
        return snapshot


def has_results() -> bool:
    with _LOCK:
        results = _STORE.get("ranked_results")
        return isinstance(results, pd.DataFrame) and not results.empty
