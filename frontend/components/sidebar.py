"""التنقل وإعدادات المسح مع دعم الخطط والمستخدم المسجل."""
from datetime import datetime
import streamlit as st


def render_sidebar():
    plan = st.session_state.get("plan_selected", "free")
    profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}

    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=70)
        st.title("🤖 AI Scanner")

        display_name = str(profile.get("full_name") or user.get("email") or "مستخدم")
        email = str(profile.get("email") or user.get("email") or "")
        st.caption(f"👤 {display_name}")
        if email and email != display_name:
            st.caption(email)

        if plan == "free":
            st.caption("🟢 الخطة المجانية")
            pages = {
                "🏠 الرئيسية المجانية": "free_home",
                "🔎 مستكشف السوق": "scanner",
                "📊 تحليل السهم": "analysis",
                "👤 حسابي": "account",
            }
        else:
            st.caption("👑 الخطة المدفوعة")
            pages = {
                "🏠 لوحة التحكم": "dashboard",
                "🔎 مستكشف السوق": "scanner",
                "📊 تحليل السهم": "analysis",
                "💧 السيولة والزخم": "flow",
                "📰 المحفزات والفرص": "catalysts",
                "⭐ قائمة المراقبة الذكية": "watchlist",
                "🔔 التنبيهات الذكية": "alerts",
                "🧠 الإشارات المتقدمة": "advanced",
                "👤 حسابي": "account",
            }

        st.markdown("---")
        st.subheader("📍 التنقل")
        labels = list(pages.keys())
        current = st.session_state.get("active_page", list(pages.values())[0])
        current_label = next((k for k, v in pages.items() if v == current), labels[0])
        selected = st.radio("التنقل الرئيسي", labels, index=labels.index(current_label), label_visibility="collapsed")
        st.session_state.active_page = pages[selected]

        if plan == "free":
            st.markdown("---")
            st.info("👑 الأدوات المتقدمة ستكون متاحة ضمن الخطة المدفوعة لاحقًا.")
        else:
            st.markdown("---")
            render_scan_settings()

        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", width="stretch", key="logout_button"):
            from supabase_auth import logout
            logout()
            st.rerun()

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
