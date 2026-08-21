"""AI Breakout Scanner - منصة متعددة الصفحات مع بوابة خطط."""
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
    "active_page": "dashboard",
    "plan_selected": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# بوابة الخطط: لا يتم تحميل بقية التطبيق قبل اختيار خطة.
if not st.session_state.get("plan_selected"):
    from frontend.pages.plan_landing import render as render_plan_landing
    render_plan_landing()
    st.stop()

try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception as exc:
    st.sidebar.warning(f"تعذر تحميل التنقل: {exc}")

page = st.session_state.get("active_page", "free_home" if st.session_state.get("plan_selected") == "free" else "dashboard")
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
except Exception as exc:
    st.title("🚀 AI Breakout Scanner")
    st.error(f"تعذر تحميل الصفحة: {exc}")

st.caption(f"آخر تحديث للواجهة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
