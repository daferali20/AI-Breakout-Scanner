"""Persistent history for strong opportunities discovered by scans."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
from threading import RLock
from typing import Any
import pandas as pd

_LOCK = RLock()
_PATH = Path("data/opportunity_history.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> list[dict[str, Any]]:
    try:
        if _PATH.exists():
            data = json.loads(_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def _save(items: list[dict[str, Any]]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(_PATH)


def _f(row: pd.Series, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def update_history(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return _load()
    with _LOCK:
        items = _load()
        by_symbol = {str(x.get("symbol", "")).upper(): x for x in items}
        now = _now()
        for _, row in frame.iterrows():
            symbol = str(row.get("symbol", row.get("ticker", ""))).strip().upper()
            score = _f(row, "final_opportunity_score", _f(row, "enhanced_opportunity_score", _f(row, "opportunity_score")))
            confidence = _f(row, "confidence_score")
            advanced = int(_f(row, "advanced_signal_count"))
            stage = str(row.get("opportunity_stage", "WATCH"))
            if not symbol or not (score >= 70 or confidence >= 75 or advanced >= 2 or stage == "CONFIRMED"):
                continue
            old = by_symbol.get(symbol)
            if old:
                previous_score = float(old.get("current_score", 0))
                previous_stage = old.get("current_stage", "WATCH")
                old.update({
                    "last_seen": now, "times_detected": int(old.get("times_detected", 0)) + 1,
                    "previous_score": previous_score, "current_score": round(score, 1),
                    "best_score": round(max(float(old.get("best_score", 0)), score), 1),
                    "previous_stage": previous_stage, "current_stage": stage,
                    "current_confidence": round(confidence, 1),
                    "best_confidence": round(max(float(old.get("best_confidence", 0)), confidence), 1),
                    "current_price": _f(row, "price"), "risk_reward": _f(row, "risk_reward"),
                    "status": "IMPROVING" if score > previous_score + 2 else ("WEAKENING" if score < previous_score - 5 else "PERSISTENT"),
                })
            else:
                by_symbol[symbol] = {
                    "symbol": symbol, "first_seen": now, "last_seen": now, "times_detected": 1,
                    "previous_score": 0.0, "current_score": round(score, 1), "best_score": round(score, 1),
                    "previous_stage": "NEW", "current_stage": stage,
                    "best_confidence": round(confidence, 1), "current_confidence": round(confidence, 1),
                    "first_price": _f(row, "price"), "current_price": _f(row, "price"),
                    "risk_reward": _f(row, "risk_reward"), "status": "NEW",
                }
        items = sorted(by_symbol.values(), key=lambda x: (float(x.get("current_score", 0)), int(x.get("times_detected", 0))), reverse=True)
        _save(items)
        return items


def get_history(status: str | None = None, query: str = "") -> list[dict[str, Any]]:
    with _LOCK:
        items = _load()
    if status:
        items = [x for x in items if x.get("status") == status]
    if query:
        q = query.strip().upper()
        items = [x for x in items if q in str(x.get("symbol", "")).upper()]
    return items
