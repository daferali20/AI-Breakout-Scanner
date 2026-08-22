"""قائمة جانبية احترافية وواضحة للمستخدم والخطة والتنقل."""
from datetime import datetime, timezone
import streamlit as st

SIDEBAR_STYLE = """
<style>
[data-testid="stSidebar"] {background:linear-gradient(180deg,#121629 0%,#171b31 55%,#111525 100%) !important;border-right:1px solid rgba(255,255,255,.07)!important;}
[data-testid="stSidebar"] > div:first-child {padding-top:.9rem!important;}
.sidebar-brand{display:flex;align-items:center;gap:12px;padding:10px 10px 14px;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,.06)}
.sidebar-brand-icon{width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#6d7cff,#8b5cf6);font-size:21px;box-shadow:0 8px 22px rgba(109,124,255,.25)}
.sidebar-brand-title{font-size:18px;font-weight:800;color:#fff;line-height:1.1}.sidebar-brand-subtitle{font-size:11px;color:#8f9bb7;margin-top:4px;letter-spacing:.35px}
.sidebar-account-card{display:flex;gap:11px;align-items:center;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);border-radius:15px;padding:12px;margin:8px 4px 16px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.sidebar-avatar{width:43px;height:43px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:white;background:linear-gradient(135deg,#3b82f6,#8b5cf6);flex:0 0 auto}.sidebar-account-meta{min-width:0}.sidebar-account-name{font-weight:800;color:#fff;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sidebar-account-email{font-size:10.5px;color:#91a0bb;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}.sidebar-badges{display:flex;gap:5px;margin-top:7px;flex-wrap:wrap}.sidebar-badge{font-size:9px;font-weight:800;letter-spacing:.45px;padding:3px 7px;border-radius:999px}.plan-free{background:rgba(34,197,94,.13);color:#74e69a;border:1px solid rgba(34,197,94,.25)}.plan-pro{background:rgba(245,158,11,.13);color:#f7c55c;border:1px solid rgba(245,158,11,.25)}.plan-trial{background:rgba(59,130,246,.15);color:#93c5fd;border:1px solid rgba(59,130,246,.28)}.role-user{background:rgba(148,163,184,.12);color:#cbd5e1;border:1px solid rgba(148,163,184,.2)}.role-admin{background:rgba(168,85,247,.14);color:#caa7ff;border:1px solid rgba(168,85,247,.28)}
.sidebar-section-title{font-size:10px;text-transform:uppercase;letter-spacing:1.4px;color:#71809d;margin:2px 9px 7px;font-weight:800}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:4px!important}
[data-testid="stSidebar"] div[role="radiogroup"] label{background:transparent!important;border:1px solid transparent!important;border-radius:11px!important;padding:8px 10px!important;min-height:40px;transition:.18s ease!important}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(109,124,255,.08)!important;border-color:rgba(109,124,255,.15)!important;transform:translateX(2px)}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,rgba(109,124,255,.17),rgba(139,92,246,.10))!important;border-color:rgba(109,124,255,.32)!important;box-shadow:inset 3px 0 0 #7180ff}
[data-testid="stSidebar"] div[role="radiogroup"] label p{font-size:13.5px!important;font-weight:650!important;color:#dfe6f3!important}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p{color:#fff!important;font-weight:800!important}
.sidebar-upgrade-card{margin:16px 4px 12px;padding:13px;border-radius:14px;background:linear-gradient(135deg,rgba(245,158,11,.10),rgba(168,85,247,.10));border:1px solid rgba(245,158,11,.18)}.sidebar-upgrade-title{font-weight:800;color:#fff;font-size:13px}.sidebar-upgrade-text{font-size:10.5px;color:#a9b5c9;margin-top:5px;line-height:1.5}
.sidebar-trial-card{margin:12px 4px;padding:11px 13px;border-radius:13px;background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.18);font-size:11px;color:#bfdbfe;line-height:1.55}
.sidebar-bottom-separator{height:1px;background:rgba(255,255,255,.06);margin:14px 4px 12px}.sidebar-footer{padding:8px 6px 4px;text-align:center;color:#68758f;font-size:9.5px;line-height:1.65}
[data-testid="stSidebar"] .stButton>button{border-radius:11px!important;min-height:40px!important;background:rgba(255,255,255,.045)!important;border:1px solid rgba(255,255,255,.08)!important;box-shadow:none!important}
[data-testid="stSidebar"] details{background:rgba(255,255,255,.025)!important;border:1px solid rgba(255,255,255,.06)!important;border-radius:12px!important}
</style>
"""


def _trial_from_profile(profile: dict) -> tuple[bool, int]:
    start_raw = profile.get("trial_started_at")
    end_raw = profile.get("trial_ends_at")
    if not start_raw or not end_raw:
        return False, 0
    try:
        start = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
        if start.tzinfo is None: start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None: end = end.replace(tzinfo=timezone.utc)
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
    st.markdown(f"""<div class="sidebar-account-card"><div class="sidebar-avatar">{name[:1].upper() if name else 'U'}</div><div class="sidebar-account-meta"><div class="sidebar-account-name">{name}</div><div class="sidebar-account-email">{email}</div><div class="sidebar-badges"><span class="sidebar-badge plan-{plan_class}">{plan_label}</span><span class="sidebar-badge role-{role}">{role_label}</span></div></div></div>""", unsafe_allow_html=True)


def render_sidebar():
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
    with st.sidebar:
        st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)
        st.markdown("""<div class="sidebar-brand"><div class="sidebar-brand-icon">📈</div><div><div class="sidebar-brand-title">AI Scanner</div><div class="sidebar-brand-subtitle">Breakout Intelligence</div></div></div>""", unsafe_allow_html=True)
        _account_card(display_name, email, plan, role, trial_active)
        if trial_active:
            st.markdown(f"<div class='sidebar-trial-card'>🎁 الفترة التجريبية مفعلة<br><b>متبقي تقريبًا {trial_days_left} يوم</b> من الوصول الكامل إلى أدوات Pro.</div>", unsafe_allow_html=True)
        if plan == "free":
            pages = {"🏠  الرئيسية":"free_home","🔎  مستكشف السوق":"scanner","📊  تحليل السهم":"analysis","👤  حسابي":"account"}
        else:
            pages = {"🏠  لوحة التحكم":"dashboard","🔎  مستكشف السوق":"scanner","📊  تحليل السهم":"analysis","💧  السيولة والزخم":"flow","📰  المحفزات والفرص":"catalysts","⭐  قائمة المراقبة":"watchlist","🔔  التنبيهات":"alerts","🧠  الإشارات المتقدمة":"advanced","👤  حسابي":"account"}
        if role == "admin": pages["🛡️  لوحة الإدارة"] = "admin"
        st.markdown('<div class="sidebar-section-title">التنقل</div>', unsafe_allow_html=True)
        labels=list(pages.keys()); current=st.session_state.get("active_page",list(pages.values())[0]); current_label=next((k for k,v in pages.items() if v==current),labels[0])
        selected=st.radio("التنقل الرئيسي",labels,index=labels.index(current_label),label_visibility="collapsed",key="main_sidebar_navigation")
        st.session_state.active_page=pages[selected]
        if plan == "free":
            st.markdown("""<div class="sidebar-upgrade-card"><div class="sidebar-upgrade-title">👑 الترقية إلى Pro</div><div class="sidebar-upgrade-text">افتح أدوات الزخم والسيولة والتنبيهات والإشارات المتقدمة.</div></div>""", unsafe_allow_html=True)
        else:
            with st.expander("⚙️ إعدادات المسح", expanded=False): render_scan_settings()
        st.markdown('<div class="sidebar-bottom-separator"></div>', unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", width="stretch", key="logout_button"):
            from supabase_auth import logout
            logout(); st.rerun()
        st.markdown(f"""<div class="sidebar-footer"><div>🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div><div>AI Breakout Scanner</div></div>""", unsafe_allow_html=True)


def render_scan_settings():
    min_score=st.slider("🎯 الحد الأدنى للفرصة",0,90,40,5,key="sidebar_min_score")
    max_symbols=st.slider("📈 عدد الأسهم",10,250,50,10,key="sidebar_max_symbols")
    st.session_state.sidebar_config={"min_score":min_score,"max_symbols":max_symbols}
    if st.button("🔍 ابدأ المسح الآن",type="primary",width="stretch",key="scan_button"):
        st.session_state.scan_requested=True; st.session_state.active_page="dashboard"; st.rerun()
