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

# -----------------------------------------------------------------------------
# Global styling (keep the existing frontend design)
# -----------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(PROJECT_ROOT, "frontend", "assets", "style.css")
if os.path.isfile(CSS_PATH):
    try:
        with open(CSS_PATH, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        pass

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "last_scan_time" not in st.session_state:
    st.session_state.last_scan_time = None

# -----------------------------------------------------------------------------
# Sidebar and existing dashboard UI
# -----------------------------------------------------------------------------
try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception as exc:
    # The dashboard must remain usable even if an optional frontend component
    # fails. Do not import the backend here: that belongs to the scan pages.
    st.sidebar.warning(f"تعذر تحميل الشريط الجانبي: {exc}")

current_page = st.session_state.get("current_page", "dashboard")

if current_page == "dashboard":
    try:
        from frontend.pages.dashboard import render
        render()
    except Exception as exc:
        st.title("🚀 AI Breakout Scanner")
        st.error(f"تعذر تحميل لوحة التحكم: {exc}")

elif current_page == "market_data":
    st.title("🌐 بيانات السوق")
    st.info("صفحة بيانات السوق متاحة من خلال صفحة التحليل/المسح المتخصصة.")

elif current_page == "scanner":
    st.title("🔍 مسح السوق")
    st.info("استخدم صفحة AI Opportunity Ranking لتشغيل محرك الفرص المتقدم.")
    st.page_link("pages/AI_Opportunity_Ranking.py", label="🏆 فتح AI Opportunity Ranking")

elif current_page == "analyze":
    st.title("📈 تحليل سهم")
    st.info("استخدم AI Opportunity Ranking لتحليل الأسهم وترتيب الفرص.")
    st.page_link("pages/AI_Opportunity_Ranking.py", label="🏆 فتح AI Opportunity Ranking")

else:
    st.session_state.current_page = "dashboard"
    st.rerun()

st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
