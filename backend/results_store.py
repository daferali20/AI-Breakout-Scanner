"""Shared in-process result store for the dashboard and scanner pages.

Streamlit session_state is scoped to a browser session. This small shared store
keeps the latest scan available when the user navigates between pages and when
multiple Streamlit page modules are involved.
"""

from __future__ import annotations

from threading import RLock
from typing import Any

import pandas as pd


_LOCK = RLock()
_STORE: dict[str, Any] = {
    "scan_results": pd.DataFrame(),
    "scan_results_all": pd.DataFrame(),
    "scan_errors": pd.DataFrame(),
    "scan_symbols_count": 0,
    "scan_success_count": 0,
    "last_scan_time": None,
    "scan_universe_source": "لم يتم إجراء مسح بعد",
    "market_regime": None,
}


def save_scan(**values: Any) -> None:
    """Replace the latest scan snapshot atomically."""
    with _LOCK:
        for key, value in values.items():
            if isinstance(value, pd.DataFrame):
                _STORE[key] = value.copy()
            else:
                _STORE[key] = value


def get_scan() -> dict[str, Any]:
    """Return a defensive copy of the latest scan snapshot."""
    with _LOCK:
        snapshot = dict(_STORE)
        for key in ("scan_results", "scan_results_all", "scan_errors"):
            if isinstance(snapshot[key], pd.DataFrame):
                snapshot[key] = snapshot[key].copy()
        return snapshot


def has_results() -> bool:
    with _LOCK:
        results = _STORE.get("scan_results")
        return isinstance(results, pd.DataFrame) and not results.empty
