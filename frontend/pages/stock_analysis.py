"""صفحة تحليل سهم متقدمة اعتمادًا على آخر نتائج المسح المحفوظة."""
from __future__ import annotations

import math
from typing import Any

import pandas as pd
import streamlit as st

from backend.results_store import get_scan


def _num(row: pd.Series, *keys: str, default: float = 0.0) -> float:
    """Read the first available numeric field safely."""
    for key in keys:
        value: Any = row.get(key, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        try:
            value = float(value)
            if math.isfinite(value):
                return value
        except (TypeError, ValueError):
            continue
    return default


@st.cache_data(ttl=900, show_spinner=False)
def _fallback_levels(symbol: str) -> dict[str, float]:
    """Calculate recent support/resistance only when scan results omitted levels."""
    try:
        import yfinance as yf
        df = yf.download(symbol, period="3mo", interval="1d", auto_adjust=False, progress=False, threads=False)
        if df is None or df.empty:
            return {}
        # yfinance may return MultiIndex columns even for one symbol.
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df = df.xs(symbol, axis=1, level=1)
            except Exception:
                try:
                    df.columns = df.columns.get_level_values(0)
                except Exception:
                    pass
        high = pd.to_numeric(df.get("High"), errors="coerce").dropna()
        low = pd.to_numeric(df.get("Low"), errors="coerce").dropna()
        close = pd.to_numeric(df.get("Close"), errors="coerce").dropna()
        if len(close) < 5 or high.empty or low.empty:
            return {}
        lookback = min(20, len(close) - 1)
        resistance = float(high.iloc[-lookback-1:-1].max()) if len(high) > lookback else float(high.iloc[:-1].max())
        support = float(low.iloc[-lookback-1:-1].min()) if len(low) > lookback else float(low.iloc[:-1].min())
        current = float(close.iloc[-1])
        return {
            "resistance": round(resistance, 2),
            "support": round(support, 2),
            "current": round(current, 2),
        }
    except Exception:
        return {}


def _score_label(value: float) -> str:
    if value >= 85:
        return "🔥 قوي جدًا"
    if value >= 70:
        return "🟢 قوي"
    if value >= 55:
        return "🟡 متوسط"
    return "🔴 ضعيف"


def _risk_label(value: float) -> str:
    if value <= 20:
        return "🟢 منخفض"
    if value <= 40:
        return "🟡 متوسط"
    return "🔴 مرتفع"


def _stage_label(row: pd.Series) -> str:
    phase = str(row.get("phase", row.get("opportunity_phase", "WATCH"))).upper()
    signal = str(row.get("signal", "WATCH")).upper()
    mapping = {
        "WATCH": "🔵 مراقبة",
        "NEAR_BREAKOUT": "🟡 يقترب من الاختراق",
        "BREAKOUT": "🚀 اختراق محتمل",
        "CONFIRMED": "🟢 اختراق مؤكد",
        "MOMENTUM": "🔥 زخم قوي",
        "BREAKOUT_READY": "🎯 جاهز للاختراق",
        "BREAKOUT_CONFIRMED": "🟢 اختراق مؤكد",
        "BUILDING": "🏗️ قيد البناء",
    }
    return mapping.get(phase, mapping.get(signal, phase.replace("_", " ").title()))


def _reasons(row: pd.Series) -> list[str]:
    reasons: list[str] = []
    momentum = _num(row, "momentum_score")
    liquidity = _num(row, "liquidity_score")
    trend = _num(row, "trend_score")
    breakout = _num(row, "breakout_probability")
    confirmation = _num(row, "confirmation_score", "confirm_score")
    rvol = _num(row, "relative_volume", "rvol", default=1.0)
    price_change = _num(row, "change_pct", "percent_change", "change")

    if momentum >= 75:
        reasons.append(f"زخم قوي ({momentum:.0f}/100)")
    if liquidity >= 75:
        reasons.append(f"سيولة قوية ({liquidity:.0f}/100)")
    if rvol >= 2:
        reasons.append(f"حجم نسبي غير اعتيادي ({rvol:.2f}x)")
    if breakout >= 75:
        reasons.append(f"احتمال اختراق مرتفع ({breakout:.0f}%)")
    if confirmation >= 75:
        reasons.append(f"تأكيد قوي ({confirmation:.0f}/100)")
    if trend >= 75:
        reasons.append(f"اتجاه داعم ({trend:.0f}/100)")
    if price_change >= 5:
        reasons.append(f"ارتفاع سعري ملحوظ (+{price_change:.2f}%)")
    return reasons or ["لم تتوافر إشارات قوية كافية في البيانات المحفوظة."]


def render() -> None:
    st.title("📊 تحليل السهم")
    st.caption("تحليل متقدم مبني على آخر مسح محفوظ، مع استكمال مستويات الدعم والمقاومة عند الحاجة.")

    snapshot = get_scan()
    data = snapshot.get("scan_results_all", pd.DataFrame())
    if not isinstance(data, pd.DataFrame) or data.empty:
        st.info("🔎 شغّل المسح من لوحة التحكم أولًا، ثم اختر سهمًا لتحليله.")
        return

    data = data.copy()
    if "symbol" not in data.columns:
        st.error("نتائج المسح لا تحتوي على رمز السهم.")
        return

    data["symbol"] = data["symbol"].astype(str).str.upper().str.strip()
    data = data[data["symbol"] != ""].drop_duplicates("symbol")
    if data.empty:
        st.info("لا توجد أسهم صالحة للتحليل.")
        return

    score_col = "opportunity_score" if "opportunity_score" in data.columns else "setup_score"
    if score_col in data.columns:
        data["__score"] = pd.to_numeric(data[score_col], errors="coerce").fillna(0)
        data = data.sort_values("__score", ascending=False)

    symbols = data["symbol"].tolist()
    default_index = 0
    query_symbol = str(st.query_params.get("symbol", "")).upper().strip()
    if query_symbol in symbols:
        default_index = symbols.index(query_symbol)

    symbol = st.selectbox("اختر السهم للتحليل", symbols, index=default_index, key="stock_analysis_symbol")
    row = data.loc[data["symbol"] == symbol].iloc[0]

    price = _num(row, "price", "current_price")
    change = _num(row, "change_pct", "percent_change", "change")
    score = _num(row, "opportunity_score", "setup_score")
    confidence = _num(row, "confidence", "confirmation_score", "confirm_score")
    breakout = _num(row, "breakout_probability")
    false_risk = _num(row, "false_breakout_risk", "false_breakout")
    momentum = _num(row, "momentum_score")
    liquidity = _num(row, "liquidity_score")
    trend = _num(row, "trend_score")
    confirmation = _num(row, "confirmation_score", "confirm_score")
    rvol = _num(row, "relative_volume", "rvol", default=1.0)

    st.markdown(f"## {symbol}")
    price_text = f"${price:,.2f}" if price else "—"
    change_text = f"{change:+.2f}%" if change else "—"
    st.caption(f"السعر: **{price_text}**  •  التغير: **{change_text}**  •  مرحلة الفرصة: **{_stage_label(row)}**")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opportunity Score", f"{score:.1f}/100", _score_label(score))
    c2.metric("Confidence", f"{confidence:.0f}/100", _score_label(confidence))
    c3.metric("Breakout Probability", f"{breakout:.0f}%")
    c4.metric("False Breakout Risk", f"{false_risk:.0f}%, {_risk_label(false_risk)}")

    st.divider()
    st.subheader("🧠 مكونات الفرصة")
    metrics = [
        ("📈 الزخم", momentum), ("💧 السيولة", liquidity), ("📊 الاتجاه", trend),
        ("🚀 الاختراق", breakout), ("✅ التأكيد", confirmation), ("💨 Relative Volume", rvol, True),
    ]
    cols = st.columns(3)
    for i, item in enumerate(metrics):
        label, value, *is_rvol = item
        if is_rvol:
            cols[i % 3].metric(label, f"{value:.2f}x")
        else:
            cols[i % 3].metric(label, f"{value:.0f}/100", _score_label(value))

    st.divider()
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("💡 لماذا ظهرت هذه الفرصة؟")
        for reason in _reasons(row):
            st.success(f"✓ {reason}")
        explanation = str(row.get("explanation", "")).strip()
        if explanation:
            st.info(explanation)

    with right:
        st.subheader("🎯 قراءة المخاطر")
        st.metric("مستوى الخطر", _risk_label(false_risk))
        if false_risk <= 20:
            st.success("خطر الاختراق الكاذب منخفض نسبيًا.")
        elif false_risk <= 40:
            st.warning("الخطر متوسط؛ يفضل انتظار تأكيد إضافي.")
        else:
            st.error("الخطر مرتفع؛ الإشارة تحتاج إلى تأكيد أقوى.")
        st.caption(f"مرحلة الفرصة: {_stage_label(row)}")

    st.divider()
    st.subheader("🎯 مستويات الفرصة")
    target = _num(row, "target", "target_price")
    support = _num(row, "support", "support_level")
    resistance = _num(row, "resistance", "resistance_level", "breakout_level", "entry", "entry_price")

    fallback = {}
    if not resistance or not support:
        fallback = _fallback_levels(symbol)
        resistance = resistance or float(fallback.get("resistance", 0) or 0)
        support = support or float(fallback.get("support", 0) or 0)
        if not price:
            price = float(fallback.get("current", 0) or 0)
            price_text = f"${price:,.2f}" if price else "—"

    p1, p2, p3 = st.columns(3)
    p1.metric("السعر الحالي", price_text)
    p2.metric("المقاومة / مستوى الاختراق", f"${resistance:,.2f}" if resistance else "غير متوفر")
    p3.metric("الهدف", f"${target:,.2f}" if target else "غير متوفر")
    if support:
        st.caption(f"الدعم: ${support:,.2f}")
    if fallback:
        st.caption("تم استكمال الدعم/المقاومة من آخر 20 جلسة لأن نتيجة المسح المحفوظة لم تتضمن هذه المستويات.")

    st.divider()
    st.subheader("📋 بيانات التحليل")
    detail = {
        "الرمز": symbol,
        "Opportunity Score": round(score, 2),
        "Confidence": round(confidence, 2),
        "Momentum": round(momentum, 2),
        "Liquidity": round(liquidity, 2),
        "Trend": round(trend, 2),
        "Breakout Probability": round(breakout, 2),
        "Confirmation": round(confirmation, 2),
        "False Breakout Risk": round(false_risk, 2),
        "Relative Volume": round(rvol, 2),
        "Resistance": round(resistance, 2) if resistance else None,
        "Support": round(support, 2) if support else None,
        "Stage": _stage_label(row),
    }
    st.dataframe(pd.DataFrame([detail]), width="stretch", hide_index=True)
