"""الواجهة الرئيسية للخطة المجانية."""
from __future__ import annotations
import pandas as pd
import streamlit as st

try:
    from backend.results_store import get_scan
except Exception:
    get_scan = None


def _go(page: str) -> None:
    st.session_state.active_page = page
    st.rerun()


def render() -> None:
    st.title("🟢 الخطة المجانية")
    st.caption("واجهة مبسطة لمتابعة السوق وتجربة أهم أدوات AI Breakout Scanner.")

    state = get_scan() if get_scan else {}
    ranked = state.get("ranked_results", pd.DataFrame()) if isinstance(state, dict) else pd.DataFrame()
    summary = state.get("opportunity_summary", {}) if isinstance(state, dict) else {}
    regime = state.get("market_regime", {}) if isinstance(state, dict) else {}

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 أسهم محللة", int(summary.get("count", len(ranked) if isinstance(ranked, pd.DataFrame) else 0) or 0))
    m2.metric("🔥 فرص قوية", int(summary.get("strong", 0) or 0))
    m3.metric("⭐ متوسط التقييم", f"{float(summary.get('average_score', 0) or 0):.1f}")
    m4.metric("🌐 حالة السوق", (regime or {}).get("label", "غير متاح") if isinstance(regime, dict) else "غير متاح")

    st.markdown("---")
    st.subheader("ابدأ من هنا")
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("### 🔎 مستكشف السوق")
            st.write("شاهد الأسهم التي نجح النظام في تحليلها واكتشف الفرص الأساسية.")
            if st.button("فتح المستكشف", width="stretch", key="free_open_scanner"):
                _go("scanner")

    with c2:
        with st.container(border=True):
            st.markdown("### 📊 تحليل سهم")
            st.write("أدخل رمز سهم وشاهد قراءة فنية مبسطة للاتجاه والزخم.")
            if st.button("تحليل سهم", width="stretch", key="free_open_analysis"):
                _go("analysis")

    with c3:
        with st.container(border=True):
            st.markdown("### 🚀 الأسهم الأكثر ارتفاعًا")
            st.write("تابع الأسهم القوية ضمن نطاقات سعرية محددة من صفحة +40% المستقلة.")
            st.page_link("pages/Strong_Gainers_40.py", label="فتح الأسهم +40%", icon="🚀", use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 لمحة عن أفضل الفرص")
    if isinstance(ranked, pd.DataFrame) and not ranked.empty:
        view = ranked.head(5).copy()
        wanted = [c for c in ["symbol", "price", "final_opportunity_score", "opportunity_score", "momentum_score", "liquidity_score", "opportunity_stage"] if c in view.columns]
        if wanted:
            st.dataframe(view[wanted], width="stretch", hide_index=True)
        else:
            st.dataframe(view, width="stretch", hide_index=True)
    else:
        st.info("لا توجد نتائج محفوظة بعد. افتح مستكشف السوق أو شغّل المسح من لوحة التحكم.")

    st.markdown("---")
    st.info("👑 أدوات مثل التنبيهات الذكية، قائمة المراقبة، المحفزات، والسجل التاريخي ستكون ضمن الخطة المدفوعة لاحقًا.")
