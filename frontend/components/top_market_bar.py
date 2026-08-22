"""Reusable top market bar for the institutional UI."""
from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


INDEX_SYMBOLS = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
    "VIX": "^VIX",
}


@st.cache_data(ttl=120, show_spinner=False)
def _market_snapshot() -> dict[str, dict[str, float | None]]:
    """Return latest value and daily percent change for the headline indexes."""
    result: dict[str, dict[str, float | None]] = {
        name: {"price": None, "change_pct": None} for name in INDEX_SYMBOLS
    }
    try:
        import yfinance as yf

        data = yf.download(
            list(INDEX_SYMBOLS.values()),
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=True,
        )
        if data is None or data.empty:
            return result

        close = data.get("Close")
        if close is None:
            return result

        if isinstance(close, pd.Series):
            close = close.to_frame()

        for label, symbol in INDEX_SYMBOLS.items():
            try:
                series = pd.to_numeric(close[symbol], errors="coerce").dropna()
                if series.empty:
                    continue
                latest = float(series.iloc[-1])
                previous = float(series.iloc[-2]) if len(series) > 1 else latest
                change = ((latest / previous) - 1.0) * 100.0 if previous else 0.0
                result[label] = {"price": latest, "change_pct": change}
            except Exception:
                continue
    except Exception:
        pass
    return result


def _market_state() -> tuple[str, str, str]:
    """Approximate regular US equity session using America/New_York time."""
    now = datetime.now(ZoneInfo("America/New_York"))
    weekday_open = now.weekday() < 5
    regular_open = time(9, 30) <= now.time() < time(16, 0)
    if weekday_open and regular_open:
        return "السوق مفتوح", "open", now.strftime("%H:%M:%S ET")
    return "السوق مغلق", "closed", now.strftime("%H:%M:%S ET")


def _fmt_price(value: float | None, label: str) -> str:
    if value is None:
        return "—"
    if label == "VIX":
        return f"{value:,.2f}"
    return f"{value:,.2f}"


def render_top_market_bar() -> None:
    snapshot = _market_snapshot()
    state_label, state_class, market_time = _market_state()

    profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}
    name = str(profile.get("full_name") or user.get("email") or "User")
    plan = str(st.session_state.get("plan_selected") or "free").upper()
    trial = bool(st.session_state.get("trial_active", False))
    plan_label = "7-DAY TRIAL" if trial else plan
    initial = name[:1].upper() if name else "U"

    market_items = []
    for label in ("S&P 500", "NASDAQ", "DOW JONES", "VIX"):
        item = snapshot.get(label, {})
        price = item.get("price")
        change = item.get("change_pct")
        change_class = "market-up" if change is not None and change >= 0 else "market-down"
        change_text = "—" if change is None else f"{change:+.2f}%"
        market_items.append(
            f'<div class="market-index"><span>{label}</span>'
            f'<div><b class="{change_class}">{change_text}</b><strong>{_fmt_price(price, label)}</strong></div></div>'
        )

    html = (
        '<div class="global-market-bar">'
        f'<div class="market-session"><i class="session-dot {state_class}"></i>'
        f'<div><b>{state_label}</b><small>{market_time}</small></div></div>'
        + ''.join(market_items)
        + '<div class="market-bar-spacer"></div>'
        + '<div class="market-account">'
        + f'<div class="market-avatar">{initial}</div>'
        + f'<div class="market-account-copy"><b>{name}</b><small>{plan_label}</small></div>'
        + '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
