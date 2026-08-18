"""الشريط الجانبي للتطبيق أحادي الصفحة."""

from datetime import datetime
import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=70)
        st.title("🤖 AI Scanner")
        st.caption("لوحة واحدة للسوق والمسح والفرص")
        st.markdown("---")

        st.subheader("📍 التطبيق")
        st.info("🏠 لوحة التحكم هي مساحة العمل الرئيسية. نتائج المسح تظهر فيها مباشرة.")

        render_scan_settings()

        st.markdown("---")
        st.caption("📈 تحليل سهم منفرد متاح داخل لوحة النتائج.")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("💡 النسخة v2.1.0 | Single Page")


def render_scan_settings():
    st.subheader("⚙️ إعدادات المسح")

    min_score = st.slider(
        "🎯 الحد الأدنى لدرجة الفرصة",
        min_value=0,
        max_value=90,
        value=40,
        step=5,
        key="sidebar_min_score",
    )

    max_symbols = st.slider(
        "📈 عدد الأسهم المستهدفة",
        min_value=10,
        max_value=250,
        value=50,
        step=10,
        key="sidebar_max_symbols",
    )

    st.session_state.sidebar_config = {
        "min_score": min_score,
        "max_symbols": max_symbols,
    }

    if st.button("🔍 ابدأ المسح الآن", type="primary", width="stretch", key="scan_button"):
        st.session_state.scan_requested = True
        st.rerun()
