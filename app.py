"""AI Breakout Scanner - single-page Streamlit application."""

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

if "last_scan_time" not in st.session_state:
    st.session_state.last_scan_time = None
if "scan_requested" not in st.session_state:
    st.session_state.scan_requested = False
if "initial_scan_done" not in st.session_state:
    st.session_state.initial_scan_done = False

try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception as exc:
    st.sidebar.warning(f"تعذر تحميل الشريط الجانبي: {exc}")

try:
    from frontend.pages.dashboard import render
    # أول دخول فقط: تشغيل اكتشاف تلقائي حتى لا تبدو الصفحة فارغة.
    # بعد ذلك يبقى التحكم يدويًا لتجنب طلبات Yahoo المتكررة أثناء rerun.
    auto_scan = not st.session_state.initial_scan_done and not st.session_state.last_scan_time
    if auto_scan:
        st.session_state.initial_scan_done = True
    render(auto_run=st.session_state.pop("scan_requested", False) or auto_scan)
except Exception as exc:
    st.title("🚀 AI Breakout Scanner")
    st.error(f"تعذر تحميل لوحة التحكم: {exc}")

st.caption(f"آخر تحديث للواجهة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
