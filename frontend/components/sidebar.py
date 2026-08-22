"""Unified, scalable institutional sidebar for AI Breakout Scanner."""
from datetime import datetime, timezone
import streamlit as st


def _trial_from_profile(profile: dict) -> tuple[bool, int]:
    start_raw = profile.get("trial_started_at")
    end_raw = profile.get("trial_ends_at")
    if not start_raw or not end_raw:
        return False, 0
    try:
        start = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        active = start.astimezone(timezone.utc) <= now < end.astimezone(timezone.utc)
        seconds = max(0, int((end.astimezone(timezone.utc) - now).total_seconds())) if active else 0
        days = (seconds + 86399) // 86400 if seconds else 0
        return active, days
    except Exception:
        return False, 0


def _account_card(name: str, email: str, plan: str, role: str, trial_active: bool) -> None:
    if trial_active:
        plan_label, plan_class = "7-DAY TRIAL", "trial"
    else:
        plan_label, plan_class = ("PRO", "pro") if plan == "pro" else ("FREE", "free")
    role_label = "ADMIN" if role == "admin" else "USER"
    initial = name[:1].upper() if name else "U"
    st.markdown(
        f'<div class="sidebar-account-card"><div class="sidebar-avatar">{initial}</div>'
        f'<div class="sidebar-account-meta"><div class="sidebar-account-name">{name}</div>'
        f'<div class="sidebar-account-email">{email}</div><div class="sidebar-badges">'
        f'<span class="sidebar-badge plan-{plan_class}">{plan_label}</span>'
        f'<span class="sidebar-badge role-{role}">{role_label}</span></div></div></div>',
        unsafe_allow_html=True,
    )


def _go_internal(target: str) -> None:
    st.session_state.active_page = target
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()


def _internal_item(label: str, target: str, active_page: str, item_id: str | None = None) -> None:
    active = active_page == target
    unique_id = item_id or target
    if st.button(
        label,
        key=f"nav_{unique_id}",
        type="primary" if active else "secondary",
        width="stretch",
    ):
        _go_internal(target)


def _external_item(label: str, path: str) -> None:
    st.page_link(path, label=label, use_container_width=True)


def _section(title: str) -> None:
    st.markdown(f'<div class="sidebar-section-title">{title}</div>', unsafe_allow_html=True)


def render_sidebar() -> None:
    profile = st.session_state.get("user_profile") or {}
    profile_trial_active, profile_trial_days = _trial_from_profile(profile)
    trial_active = profile_trial_active or bool(st.session_state.get("trial_active", False))
    trial_days_left = profile_trial_days if profile_trial_active else int(st.session_state.get("trial_days_left", 0) or 0)
    paid_status = str(profile.get("subscription_status", "free") or "free").lower()
    plan = "pro" if paid_status == "pro" or trial_active else "free"
    st.session_state.trial_active = trial_active
    st.session_state.trial_days_left = trial_days_left
    st.session_state.plan_selected = plan

    user = st.session_state.get("auth_user") or {}
    role = str(profile.get("role", "user") or "user").lower()
    display_name = str(profile.get("full_name") or user.get("email") or "مستخدم")
    email = str(profile.get("email") or user.get("email") or "")
    active_page = str(st.session_state.get("active_page") or "dashboard")

    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="sidebar-brand-icon">📈</div><div>'
            '<div class="sidebar-brand-title">AI BREAKOUT</div>'
            '<div class="sidebar-brand-title brand-accent">SCANNER</div>'
            '<div class="sidebar-brand-subtitle">Breakout Intelligence</div></div></div>',
            unsafe_allow_html=True,
        )
        _account_card(display_name, email, plan, role, trial_active)

        _section("اكتشاف الفرص")
        _internal_item(
            "🏠  لوحة التحكم",
            "dashboard" if plan == "pro" else "free_home",
            active_page,
            item_id="home_dashboard",
        )
        if plan == "pro":
            _internal_item("🧠  AI Scanner", "dashboard", active_page, item_id="ai_scanner")
            _external_item("🚀  الأكثر ارتفاعًا", "pages/Strong_Gainers_40.py")
            _external_item("📡  متصدرو السوق", "pages/Live_Market_Leaders.py")
            _external_item("⭐  ترتيب الفرص", "pages/AI_Opportunity_Ranking.py")
            _external_item("🕘  الفرص التاريخية", "pages/Historical_Opportunities.py")
        else:
            _internal_item("🔎  مستكشف السوق", "scanner", active_page, item_id="free_scanner")

        _section("التحليل")
        _internal_item("📊  تحليل السهم", "analysis", active_page, item_id="stock_analysis")
        if plan == "pro":
            _internal_item("🔎  مستكشف السوق", "scanner", active_page, item_id="market_scanner")
            _internal_item("💧  تدفق السيولة", "flow", active_page, item_id="liquidity_flow")
            _internal_item("📰  المحفزات والفرص", "catalysts", active_page, item_id="catalysts")
            _internal_item("🧠  الإشارات المتقدمة", "advanced", active_page, item_id="advanced_signals")

        _section("الأدوات")
        if plan == "pro":
            _internal_item("⭐  قائمة المراقبة", "watchlist", active_page, item_id="watchlist")
            _internal_item("🔔  التنبيهات", "alerts", active_page, item_id="alerts")
        _internal_item("👤  حسابي", "account", active_page, item_id="account")

        if role == "admin":
            _section("الإدارة")
            _internal_item("🛡️  لوحة الإدارة", "admin", active_page, item_id="admin_panel")

        if plan == "free":
            st.markdown(
                '<div class="sidebar-upgrade-card"><div class="sidebar-upgrade-title">👑 Pro Access</div>'
                '<div class="sidebar-upgrade-text">افتح أدوات اكتشاف المتصدرين والسيولة والزخم والتنبيهات.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            with st.expander("⚙️ إعدادات المسح", expanded=False):
                render_scan_settings()

        if trial_active:
            pct = max(0, min(100, round((trial_days_left / 7) * 100)))
            st.markdown(
                f'<div class="sidebar-trial-card"><div class="trial-row"><b>👑 7-Day Trial</b>'
                f'<span>{trial_days_left} days left</span></div><div class="trial-caption">Full Pro access</div>'
                f'<div class="trial-progress"><span style="width:{pct}%"></span></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-bottom-separator"></div>', unsafe_allow_html=True)
        _internal_item("🔒  سياسة الخصوصية", "privacy", active_page, item_id="privacy_policy")
        _internal_item("📜  الشروط والأحكام", "terms", active_page, item_id="terms_conditions")

        if st.button("🚪 تسجيل الخروج", width="stretch", key="logout_button"):
            from supabase_auth import logout
            logout()
            st.rerun()

        st.markdown(
            f"<div class='sidebar-footer'>{datetime.now().strftime('%Y-%m-%d %H:%M')}<br>AI Breakout Scanner · Privacy · Terms</div>",
            unsafe_allow_html=True,
        )


def render_scan_settings():
    min_score = st.slider("🎯 الحد الأدنى للفرصة", 0, 90, 40, 5, key="sidebar_min_score")
    max_symbols = st.slider("📈 عدد الأسهم", 10, 250, 50, 10, key="sidebar_max_symbols")
    st.session_state.sidebar_config = {"min_score": min_score, "max_symbols": max_symbols}
    if st.button("🔍 ابدأ المسح الآن", type="primary", width="stretch", key="scan_button"):
        st.session_state.scan_requested = True
        st.session_state.active_page = "dashboard"
        try:
            st.switch_page("app.py")
        except Exception:
            st.rerun()
