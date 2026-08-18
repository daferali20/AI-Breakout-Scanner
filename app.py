"""AI Breakout Scanner - Streamlit entry point."""

import os
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="AI Breakout Scanner | ماسح الانفجار السعري",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(PROJECT_ROOT, "frontend", "assets", "style.css")
if os.path.isfile(CSS_PATH):
    try:
        with open(CSS_PATH, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        pass

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "last_scan_time" not in st.session_state:
    st.session_state.last_scan_time = None

try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception as exc:
    st.sidebar.warning(f"تعذر تحميل الشريط الجانبي: {exc}")

current_page = st.session_state.get("current_page", "dashboard")

if current_page == "dashboard":
    try:
        from frontend.pages.dashboard import render
        render()
    except Exception as exc:
        st.title("🚀 AI Breakout Scanner")
        st.error(f"تعذر تحميل لوحة التحكم: {exc}")

elif current_page in {"scanner", "analyze", "market_data"}:
    # Keep the existing UI and use the specialized scanner page as the
    # single entry point for market scanning, analysis and market data.
    st.switch_page("pages/AI_Opportunity_Ranking.py")

else:
    st.session_state.current_page = "dashboard"
    st.rerun()

st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
