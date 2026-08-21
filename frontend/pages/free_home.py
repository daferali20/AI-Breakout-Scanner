"""الواجهة الرئيسية الاحترافية للخطة المجانية."""
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


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def render() -> None:
    st.markdown(
        """
        <div style="padding:22px 24px;border:1px solid rgba(120,120,120,.18);border-radius:20px;margin-bottom:18px;">
            <div style="font-size:14px;opacity:.75;margin-bottom:6px;">AI BREAKOUT SCANNER · FREE</div>
            <div style="font-size:34px;font-weight:800;line-height:1.15;">اكتشف حركة السوق بسرعة</div>
            <div style="font-size:16px;opacity:.8;margin-top:8px;">واجهة مجانية مبسطة لمتابعة أبرز الفرص، تحليل الأسهم، ورصد الارتفاعات القوية.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    state = get_scan() if get_scan else {}
    ranked = state.get("ranked_results", pd.DataFrame()) if isinstance(state, dict) else pd.DataFrame()
    summary = state.get("opportunity_summary", {}) if isinstance(state, dict) else {}
    regime = state.get("market_regime", {}) if isinstance(state, dict) else {}

    total = int(summary.get("count", len(ranked) if isinstance(ranked, pd.DataFrame) else 0) or 0)
    strong = int(summary.get("strong", 0) or 0)
    average = _num(summary.get("average_score", 0))
    market_label = (regime or {}).get("label", "غير متاح") if isinstance(regime, dict) else "غير متاح"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 الأسهم المحللة", total)
    m2.metric("🔥 الفرص القوية", strong)
    m3.metric("⭐ متوسط التقييم", f"{average:.1f}")
    m4.metric("🌐 حالة السوق", market_label)

    st.markdown("---")
    st.subheader("⚡ الوصول السريع")
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("### 🔎 مستكشف السوق")
            st.caption("استعرض نتائج المسح الأساسية ورتب الأسهم حسب جودة الفرصة.")
            if st.button("فتح مستكشف السوق", width="stretch", key="free_open_scanner"):
                _go("scanner")

    with c2:
        with st.container(border=True):
            st.markdown("### 📊 تحليل سهم")
            st.caption("ابحث برمز سهم واحصل على قراءة مبسطة للاتجاه والزخم.")
            if st.button("تحليل سهم الآن", width="stretch", key="free_open_analysis"):
                _go("analysis")

    with c3:
        with st.container(border=True):
            st.markdown("### 🚀 الأسهم +40%")
            st.caption("تابع الأسهم ذات الارتفاعات الاستثنائية ضمن نطاقات السعر المحددة.")
            st.page_link("pages/Strong_Gainers_40.py", label="فتح الأسهم +40%", icon="🚀", width="stretch")

    st.markdown("---")
    st.subheader("🏆 أفضل 5 فرص الآن")

    if isinstance(ranked, pd.DataFrame) and not ranked.empty:
        score_col = "final_opportunity_score" if "final_opportunity_score" in ranked.columns else "opportunity_score"
        work = ranked.copy()
        if score_col in work.columns:
            work[score_col] = pd.to_numeric(work[score_col], errors="coerce").fillna(0)
            work = work.sort_values(score_col, ascending=False)
        top5 = work.head(5).reset_index(drop=True)

        for idx, row in top5.iterrows():
            symbol = str(row.get("symbol", "—"))
            price = _num(row.get("price", 0))
            score = _num(row.get(score_col, 0))
            momentum = _num(row.get("momentum_score", 0))
            liquidity = _num(row.get("liquidity_score", 0))
            stage = str(row.get("opportunity_stage", "WATCH"))

            with st.container(border=True):
                a, b, c, d, e = st.columns([0.7, 1.3, 1, 1, 1.3])
                a.markdown(f"## #{idx + 1}")
                b.markdown(f"### {symbol}\n${price:.2f}" if price else f"### {symbol}")
                c.metric("🏆 التقييم", f"{score:.1f}")
                d.metric("⚡ الزخم", f"{momentum:.0f}")
                e.metric("💧 السيولة", f"{liquidity:.0f}")
                st.caption(f"مرحلة الفرصة: {stage}")
    else:
        st.info("لا توجد نتائج محفوظة حتى الآن. افتح مستكشف السوق لبدء التحليل.")

    st.markdown("---")
    st.subheader("🟢 ما الذي تحصل عليه مجانًا؟")
    f1, f2, f3, f4 = st.columns(4)
    f1.success("🔎 استكشاف السوق\n\nنتائج وفرص أساسية")
    f2.success("📊 تحليل سهم\n\nقراءة فنية مبسطة")
    f3.success("🚀 +40% Gainers\n\nرصد الارتفاعات القوية")
    f4.success("🏆 Top 5\n\nأفضل الفرص الحالية")

    st.markdown("---")
    st.subheader("👑 ماذا تضيف خطة Pro؟")
    p1, p2 = st.columns([1.6, 1])
    with p1:
        with st.container(border=True):
            st.markdown("### أدوات أعمق للمستخدم المتقدم")
            st.markdown(
                """
                - 🔔 تنبيهات ذكية عند تغير حالة الفرصة
                - ⭐ قائمة مراقبة ذكية ومستمرة
                - 💧 تحليل السيولة والزخم المتقدم
                - 🧠 إشارات متقدمة وBreakout / Retest / Squeeze
                - 📰 المحفزات والأخبار المؤثرة
                - 📚 سجل الفرص التي تم استخراجها سابقًا
                - 🎯 Risk / Reward وOpportunity Lifecycle
                """
            )
    with p2:
        with st.container(border=True):
            st.markdown("### 👑 Pro")
            st.write("مصممة للمتابعة اليومية واكتشاف الفرص بصورة أعمق.")
            st.metric("الحالة", "قريبًا")
            if st.button("عرض الخطط", width="stretch", key="free_view_plans"):
                st.session_state.selected_plan = None
                st.session_state.active_page = "plans"
                st.rerun()

    st.caption("الخطة المجانية لا تغيّر أو تحذف أيًا من أدوات المنصة المتقدمة؛ يتم فقط تقييد الوصول إليها حسب الخطة.")
