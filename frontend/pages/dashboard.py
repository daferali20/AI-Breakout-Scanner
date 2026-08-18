# frontend/pages/dashboard.py
"""لوحة التحكم الرئيسية: تعرض آخر نتائج المسح في أول نظرة."""

import streamlit as st
import pandas as pd
import plotly.express as px

from backend.results_store import get_scan


def _snapshot():
    """Use the shared scan store first, then session_state as a fallback."""
    shared = get_scan()
    if shared.get("last_scan_time"):
        return shared
    return {
        "scan_results": st.session_state.get("scan_results", pd.DataFrame()),
        "scan_results_all": st.session_state.get("scan_results_all", pd.DataFrame()),
        "scan_errors": st.session_state.get("scan_errors", pd.DataFrame()),
        "scan_symbols_count": st.session_state.get("scan_symbols_count", 0),
        "scan_success_count": st.session_state.get("scan_success_count", 0),
        "last_scan_time": st.session_state.get("last_scan_time"),
        "scan_universe_source": st.session_state.get("scan_universe_source", "لم يتم إجراء مسح بعد"),
        "market_regime": st.session_state.get("market_regime"),
    }


def render():
    snapshot = _snapshot()
    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.subheader("📊 لوحة التحكم - نظرة عامة على السوق")
    with col_time:
        last_scan = snapshot.get("last_scan_time") or "لم يتم"
        st.caption(f"🕐 آخر تحديث: {last_scan}")

    display_metrics(snapshot)
    st.markdown("---")
    display_market_status(snapshot)
    st.markdown("---")
    display_top_opportunities(snapshot)
    st.markdown("---")
    display_activity(snapshot)


def _results(snapshot=None):
    snapshot = snapshot or _snapshot()
    results = snapshot.get("scan_results", pd.DataFrame())
    return results.copy() if isinstance(results, pd.DataFrame) else pd.DataFrame()


def display_metrics(snapshot=None):
    snapshot = snapshot or _snapshot()
    results = _results(snapshot)
    total_stocks = int(snapshot.get("scan_success_count", 0))
    opportunities = len(results)
    avg_score = 0.0
    if not results.empty and "opportunity_score" in results.columns:
        avg_score = float(pd.to_numeric(results["opportunity_score"], errors="coerce").mean())
    strong_signals = 0
    if not results.empty and "signal_quality" in results.columns:
        strong_signals = int(results["signal_quality"].astype(str).str.contains("STRONG|قوي|BUY|شراء", case=False, na=False).sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _metric_card("📈", total_stocks, "أسهم تم تحليلها")
    with col2:
        _metric_card("🔥", opportunities, "فرص مكتشفة 🎯", "#00E676" if opportunities else "#FF5252")
    with col3:
        _metric_card("⭐", f"{avg_score:.1f}%", "متوسط درجة الفرصة", "#FFD700")
    with col4:
        _metric_card("🚀", strong_signals, "إشارات قوية", "#29B6F6")


def _metric_card(icon, value, label, color=None):
    style = f' style="color:{color};"' if color else ""
    st.markdown(
        f'<div class="metric-card"><div class="icon">{icon}</div>'
        f'<div class="value"{style}>{value}</div><div class="label">{label}</div></div>',
        unsafe_allow_html=True,
    )


def display_market_status(snapshot=None):
    snapshot = snapshot or _snapshot()
    st.subheader("🌐 حالة السوق")
    regime = snapshot.get("market_regime")
    source = snapshot.get("scan_universe_source", "لم يتم إجراء مسح بعد")
    errors = snapshot.get("scan_errors", pd.DataFrame())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("المصدر", source)
    with c2:
        st.metric("حالة السوق", regime.get("regime", "غير متاح") if isinstance(regime, dict) else "غير متاح")
    with c3:
        st.metric("تم تحليلها", snapshot.get("scan_success_count", 0))
    with c4:
        st.metric("تعذر تحليلها", len(errors) if isinstance(errors, pd.DataFrame) else 0)
    if _results(snapshot).empty:
        st.info("🔎 لم يتم تنفيذ مسح بعد. افتح «ابدأ المسح الآن» وشغّل المسح التلقائي، ثم ستظهر النتائج هنا تلقائيًا.")
    else:
        st.caption("النتائج أدناه هي آخر مسح محفوظ، وتُستخدم أيضًا في صفحات الترتيب والتحليل.")


def display_top_opportunities(snapshot=None):
    results = _results(snapshot)
    st.subheader("🔥 أفضل الفرص الآن")
    if results.empty:
        st.info("لا توجد نتائج محفوظة حاليًا.")
        return
    preferred = ["rank", "symbol", "price", "opportunity_score", "signal_quality", "breakout_probability", "false_breakout_risk", "relative_volume", "phase", "recommendation"]
    cols = [c for c in preferred if c in results.columns]
    display = results[cols].copy().head(10)
    display = display.rename(columns={
        "rank": "#", "symbol": "السهم", "price": "السعر", "opportunity_score": "الفرصة",
        "signal_quality": "الجودة", "breakout_probability": "احتمال الاختراق",
        "false_breakout_risk": "خطر الاختراق الكاذب", "relative_volume": "Relative Volume",
        "phase": "المرحلة", "recommendation": "الإشارة"
    })
    st.dataframe(display, width="stretch", hide_index=True, height=min(430, 80 + len(display) * 35))


def display_activity(snapshot=None):
    results = _results(snapshot)
    st.subheader("⚡ نشاط الفرص والسيولة")
    if results.empty:
        st.info("سيظهر النشاط بعد أول مسح للسوق.")
        return
    col1, col2 = st.columns(2)
    with col1:
        if "relative_volume" in results.columns:
            chart = results[["symbol", "relative_volume"]].copy()
            chart["relative_volume"] = pd.to_numeric(chart["relative_volume"], errors="coerce")
            chart = chart.dropna().sort_values("relative_volume", ascending=False).head(10)
            if not chart.empty:
                st.plotly_chart(px.bar(chart, x="symbol", y="relative_volume", title="أعلى Relative Volume"), width="stretch")
    with col2:
        if "opportunity_score" in results.columns:
            chart = results[["symbol", "opportunity_score"]].copy()
            chart["opportunity_score"] = pd.to_numeric(chart["opportunity_score"], errors="coerce")
            chart = chart.dropna().sort_values("opportunity_score", ascending=False).head(10)
            if not chart.empty:
                fig = px.bar(chart, x="symbol", y="opportunity_score", title="أعلى Opportunity Score")
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, width="stretch")
    if st.button("🔄 العودة إلى المسح وتحديث النتائج", width="stretch"):
        st.switch_page("pages/AI_Opportunity_Ranking.py")


def display_charts():
    display_activity()


def display_scan_results():
    display_top_opportunities()
