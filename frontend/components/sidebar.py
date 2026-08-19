"""التنقل وإعدادات المسح."""
from datetime import datetime
import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=70)
        st.title("🤖 AI Scanner")
        st.caption("منصة واحدة لاكتشاف وتحليل فرص السوق")
        st.markdown("---")
        st.subheader("📍 التنقل")
        pages = {
            "🏠 لوحة التحكم": "dashboard",
            "🔎 مستكشف السوق": "scanner",
            "📊 تحليل السهم": "analysis",
            "💧 السيولة والزخم": "flow",
            "📰 المحفزات والفرص": "catalysts",
        }
        labels = list(pages.keys())
        current = st.session_state.get("active_page", "dashboard")
        current_label = next((k for k, v in pages.items() if v == current), labels[0])
        selected = st.radio("", labels, index=labels.index(current_label), label_visibility="collapsed")
        st.session_state.active_page = pages[selected]
        st.markdown("---")
        render_scan_settings()
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("💡 AI Breakout Scanner | Multi-View")


def render_scan_settings():
    st.subheader("⚙️ إعدادات المسح")
    min_score = st.slider("🎯 الحد الأدنى لدرجة الفرصة", 0, 90, 40, 5, key="sidebar_min_score")
    max_symbols = st.slider("📈 عدد الأسهم المستهدفة", 10, 250, 50, 10, key="sidebar_max_symbols")
    st.session_state.sidebar_config = {"min_score": min_score, "max_symbols": max_symbols}
    if st.button("🔍 ابدأ المسح الآن", type="primary", width="stretch", key="scan_button"):
        st.session_state.scan_requested = True
        st.session_state.active_page = "dashboard"
        st.rerun()
