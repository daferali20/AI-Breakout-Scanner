"""قائمة جانبية احترافية وواضحة للمستخدم والخطة والتنقل."""
from datetime import datetime
import streamlit as st


def _account_card(name: str, email: str, plan: str, role: str) -> None:
    plan_label = "PRO" if plan == "pro" else "FREE"
    role_label = "ADMIN" if role == "admin" else "USER"
    st.markdown(
        f"""
        <div class="sidebar-account-card">
            <div class="sidebar-avatar">{name[:1].upper() if name else 'U'}</div>
            <div class="sidebar-account-meta">
                <div class="sidebar-account-name">{name}</div>
                <div class="sidebar-account-email">{email}</div>
                <div class="sidebar-badges">
                    <span class="sidebar-badge plan-{plan}">{plan_label}</span>
                    <span class="sidebar-badge role-{role}">{role_label}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    plan = st.session_state.get("plan_selected", "free")
    profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}
    role = str(profile.get("role", "user") or "user").lower()
    display_name = str(profile.get("full_name") or user.get("email") or "مستخدم")
    email = str(profile.get("email") or user.get("email") or "")

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">📈</div>
                <div>
                    <div class="sidebar-brand-title">AI Scanner</div>
                    <div class="sidebar-brand-subtitle">Breakout Intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _account_card(display_name, email, plan, role)

        if plan == "free":
            pages = {
                "🏠  الرئيسية": "free_home",
                "🔎  مستكشف السوق": "scanner",
                "📊  تحليل السهم": "analysis",
                "👤  حسابي": "account",
            }
        else:
            pages = {
                "🏠  لوحة التحكم": "dashboard",
                "🔎  مستكشف السوق": "scanner",
                "📊  تحليل السهم": "analysis",
                "💧  السيولة والزخم": "flow",
                "📰  المحفزات والفرص": "catalysts",
                "⭐  قائمة المراقبة": "watchlist",
                "🔔  التنبيهات": "alerts",
                "🧠  الإشارات المتقدمة": "advanced",
                "👤  حسابي": "account",
            }
        if role == "admin":
            pages["🛡️  لوحة الإدارة"] = "admin"

        st.markdown('<div class="sidebar-section-title">التنقل</div>', unsafe_allow_html=True)
        labels = list(pages.keys())
        current = st.session_state.get("active_page", list(pages.values())[0])
        current_label = next((k for k, v in pages.items() if v == current), labels[0])
        selected = st.radio(
            "التنقل الرئيسي",
            labels,
            index=labels.index(current_label),
            label_visibility="collapsed",
            key="main_sidebar_navigation",
        )
        st.session_state.active_page = pages[selected]

        if plan == "free":
            st.markdown(
                """
                <div class="sidebar-upgrade-card">
                    <div class="sidebar-upgrade-title">👑 الترقية إلى Pro</div>
                    <div class="sidebar-upgrade-text">افتح أدوات الزخم والسيولة والتنبيهات والإشارات المتقدمة.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            with st.expander("⚙️ إعدادات المسح", expanded=False):
                render_scan_settings()

        st.markdown('<div class="sidebar-bottom-separator"></div>', unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", width="stretch", key="logout_button"):
            from supabase_auth import logout
            logout()
            st.rerun()

        st.markdown(
            f"""
            <div class="sidebar-footer">
                <div>🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div>AI Breakout Scanner</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_scan_settings():
    min_score = st.slider("🎯 الحد الأدنى للفرصة", 0, 90, 40, 5, key="sidebar_min_score")
    max_symbols = st.slider("📈 عدد الأسهم", 10, 250, 50, 10, key="sidebar_max_symbols")
    st.session_state.sidebar_config = {"min_score": min_score, "max_symbols": max_symbols}
    if st.button("🔍 ابدأ المسح الآن", type="primary", width="stretch", key="scan_button"):
        st.session_state.scan_requested = True
        st.session_state.active_page = "dashboard"
        st.rerun()
