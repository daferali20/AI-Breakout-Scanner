"""AI Breakout Scanner - منصة متعددة الصفحات مع مصادقة Supabase وصلاحيات الخطط."""
import os
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="AI Breakout Scanner | ماسح الفرص", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(PROJECT_ROOT, "frontend", "assets", "style.css")
if os.path.isfile(CSS_PATH):
    try:
        with open(CSS_PATH, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        pass

for key, default in {
    "last_scan_time": None,
    "scan_requested": False,
    "initial_scan_done": False,
    "active_page": "auth",
    "plan_selected": None,
    "auth_user": None,
    "user_profile": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.get("auth_user"):
    from auth_page import render as render_auth
    render_auth()
    st.stop()

try:
    from supabase_auth import refresh_profile
    profile = refresh_profile()
except Exception:
    profile = st.session_state.get("user_profile") or {}

status = str(profile.get("subscription_status", "free") or "free").lower()
role = str(profile.get("role", "user") or "user").lower()
actual_plan = "pro" if status == "pro" else "free"
st.session_state.plan_selected = actual_plan

if st.session_state.get("active_page") in (None, "auth"):
    st.session_state.active_page = "dashboard" if actual_plan == "pro" else "free_home"

FREE_PAGES = {"free_home", "scanner", "analysis", "account"}
PRO_PAGES = {"dashboard", "scanner", "analysis", "flow", "catalysts", "watchlist", "alerts", "advanced", "account"}
allowed_pages = PRO_PAGES if actual_plan == "pro" else FREE_PAGES
if role == "admin":
    allowed_pages = allowed_pages | {"admin"}

requested_page = st.session_state.get("active_page", "free_home" if actual_plan == "free" else "dashboard")
if requested_page not in allowed_pages:
    st.session_state.active_page = "account"
    st.warning("🔒 لا تملك صلاحية الوصول إلى هذه الصفحة.")

try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception as exc:
    st.sidebar.warning(f"تعذر تحميل التنقل: {exc}")

page = st.session_state.get("active_page", "free_home" if actual_plan == "free" else "dashboard")
try:
    if page == "free_home":
        from frontend.pages.free_home import render
        render()
    elif page == "dashboard":
        from frontend.pages.dashboard import render
        auto_scan = not st.session_state.initial_scan_done and not st.session_state.last_scan_time
        if auto_scan:
            st.session_state.initial_scan_done = True
        render(auto_run=st.session_state.pop("scan_requested", False) or auto_scan)
    elif page == "scanner":
        from frontend.pages.market_scanner import render
        render()
    elif page == "analysis":
        from frontend.pages.stock_analysis import render
        render()
    elif page == "flow":
        from frontend.pages.liquidity_momentum import render
        render()
    elif page == "catalysts":
        from frontend.pages.catalysts import render
        render()
    elif page == "watchlist":
        from frontend.pages.smart_watchlist import render
        render()
    elif page == "alerts":
        from frontend.pages.alerts import render
        render()
    elif page == "advanced":
        from frontend.pages.advanced_signals import render
        render()
    elif page == "account":
        from frontend.pages.account import render
        render()
    elif page == "admin":
        from frontend.pages.admin import render
        render()
except Exception as exc:
    st.title("🚀 AI Breakout Scanner")
    st.error(f"تعذر تحميل الصفحة: {exc}")

st.caption(f"آخر تحديث للواجهة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
