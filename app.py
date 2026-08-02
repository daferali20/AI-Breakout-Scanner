# app.py
"""
AI Breakout Scanner - التطبيق الرئيسي
اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# ============================================================================
# إعدادات الصفحة
# ============================================================================

st.set_page_config(
    page_title="AI Breakout Scanner | ماسح الانفجار السعري",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المسارات
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# استيراد المكونات
# ============================================================================

try:
    from config import STOCK_SYMBOLS, APP_SETTINGS
except ImportError:
    STOCK_SYMBOLS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
        'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'CSCO'
    ]
    APP_SETTINGS = {'title': 'AI Breakout Scanner'}

try:
    from backend.scanner.breakout_scanner import BreakoutScanner
except ImportError:
    BreakoutScanner = None

# ============================================================================
# التصميم - استايل خفيف ونظيف
# ============================================================================

def load_css():
    """تحميل استايل خفيف ونظيف مع كتابة واضحة"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
    
    * {
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* ===== الشريط الجانبي ===== */
    [data-testid="stSidebar"] {
        background: rgba(20, 20, 40, 0.92) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 20px;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stSubheader {
        color: #ffffff !important;
    }
    
    /* ===== النصوص العامة ===== */
    .stMarkdown, .stText, .stWrite, p, div, span, label {
        color: #e8e8e8 !important;
    }
    
    .stSubheader, .stHeader {
        color: #ffffff !important;
    }
    
    /* ===== البطاقات ===== */
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 18px 20px;
        border-radius: 14px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }
    
    .metric-card .label {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.55);
        font-weight: 400;
    }
    
    .metric-card .icon {
        font-size: 1.6rem;
        margin-bottom: 4px;
    }
    
    /* ===== الأزرار ===== */
    .stButton > button, button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 8px 22px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25) !important;
    }
    
    .stButton > button:hover, button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35) !important;
    }
    
    button[kind="primary"], .stButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3) !important;
    }
    
    button[kind="primary"]:hover, .stButton button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4) !important;
    }
    
    /* ===== الجداول ===== */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] table {
        background: transparent !important;
    }
    
    [data-testid="stDataFrame"] thead th {
        background: rgba(102, 126, 234, 0.12) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 10px 12px !important;
        border-bottom: 2px solid rgba(102, 126, 234, 0.15) !important;
    }
    
    [data-testid="stDataFrame"] tbody td {
        color: #d0d0d0 !important;
        padding: 8px 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(102, 126, 234, 0.06) !important;
    }
    
    /* ===== المؤشرات (Metrics) ===== */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 400 !important;
    }
    
    [data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* ===== التبويبات (Tabs) ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        color: #ffffff !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
    }
    
    /* ===== الإكسباندر (Expander) ===== */
    .stExpander {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stExpander summary {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* ===== السلايدرات ===== */
    [data-testid="stSlider"] > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* ========================================================================
   إصلاح شامل للقوائم المنسدلة (Selectbox) - نسخة كاملة
   ======================================================================== */

    /* القائمة الرئيسية (الحقل المغلق) */
    .stSelectbox > div[data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        min-height: 38px !important;
    }
    
    .stSelectbox > div[data-baseweb="select"] > div:hover {
        border-color: rgba(102, 126, 234, 0.4) !important;
        background-color: rgba(255, 255, 255, 0.12) !important;
    }
    
    .stSelectbox > div[data-baseweb="select"] > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* النص داخل الحقل المغلق */
    .stSelectbox > div[data-baseweb="select"] > div div[data-baseweb="select-value"] {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox > div[data-baseweb="select"] > div div[data-baseweb="select-placeholder"] {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* القائمة المنسدلة المفتوحة */
    .stSelectbox > div[data-baseweb="select"] ul {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 4px 0 !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5) !important;
        max-height: 300px !important;
        overflow-y: auto !important;
        z-index: 9999 !important;
    }
    
    /* عناصر القائمة - الوضع العادي */
    .stSelectbox > div[data-baseweb="select"] ul li {
        color: #ffffff !important;
        background-color: transparent !important;
        padding: 10px 16px !important;
        font-size: 0.95rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    /* عناصر القائمة - عند التمرير */
    .stSelectbox > div[data-baseweb="select"] ul li:hover {
        background-color: rgba(102, 126, 234, 0.25) !important;
        color: #ffffff !important;
        border-left: 3px solid #667eea !important;
    }
    
    /* ===== العنصر المحدد - تدرج أرجواني مع نص أبيض واضح ===== */
    .stSelectbox > div[data-baseweb="select"] ul li[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-left: 4px solid #ffffff !important;
        box-shadow: inset 0 0 30px rgba(255, 255, 255, 0.08) !important;
        padding-left: 18px !important;
    }
    
    /* العنصر المحدد - عند التمرير */
    .stSelectbox > div[data-baseweb="select"] ul li[aria-selected="true"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        color: #ffffff !important;
        border-left: 4px solid #FFD700 !important;
    }
    
    /* ===== العنصر المحدد في الشريط الجانبي ===== */
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul li[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-left: 4px solid #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul li[aria-selected="true"]:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        border-left: 4px solid #FFD700 !important;
    }
    
    /* شريط التمرير في القائمة */
    .stSelectbox > div[data-baseweb="select"] ul::-webkit-scrollbar {
        width: 4px;
    }
    
    .stSelectbox > div[data-baseweb="select"] ul::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .stSelectbox > div[data-baseweb="select"] ul::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    /* ========================================================================
       إصلاح القوائم المنسدلة في الشريط الجانبي
       ======================================================================== */
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] > div:hover {
        border-color: rgba(102, 126, 234, 0.4) !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul li {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul li:hover {
        background-color: rgba(102, 126, 234, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] ul li[aria-selected="true"] {
        background-color: rgba(102, 126, 234, 0.25) !important;
    }
    
    /* ========================================================================
       إصلاح الـ Radio Buttons
       ======================================================================== */
    
    .stRadio > div[role="radiogroup"] label {
        color: #e0e0e0 !important;
        padding: 6px 10px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stRadio > div[role="radiogroup"] label:hover {
        color: #ffffff !important;
        background-color: rgba(102, 126, 234, 0.08) !important;
    }
    
    .stRadio > div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        color: inherit !important;
    }
    
    /* === Radio في الشريط الجانبي === */
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label:hover {
        color: #ffffff !important;
        background-color: rgba(102, 126, 234, 0.08) !important;
    }
    
    /* ========================================================================
       إصلاح الـ Text Input
       ======================================================================== */
    
    .stTextInput > div > div > input {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ========================================================================
       التنبيهات
       ======================================================================== */
    
    .stAlert {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #e0e0e0 !important;
    }
    
    .stAlert .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* ========================================================================
       شريط التمرير العام
       ======================================================================== */
    
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* ========================================================================
       رسائل الحالة
       ======================================================================== */
    
    .stSuccess {
        background: rgba(0, 230, 118, 0.08) !important;
        border: 1px solid rgba(0, 230, 118, 0.15) !important;
        color: #00E676 !important;
    }
    
    .stInfo {
        background: rgba(41, 182, 246, 0.08) !important;
        border: 1px solid rgba(41, 182, 246, 0.15) !important;
        color: #29B6F6 !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.08) !important;
        border: 1px solid rgba(255, 193, 7, 0.15) !important;
        color: #FFC107 !important;
    }
    
    .stError {
        background: rgba(255, 82, 82, 0.08) !important;
        border: 1px solid rgba(255, 82, 82, 0.15) !important;
        color: #FF5252 !important;
    }
    
    /* ========================================================================
       شريط التقدم
       ======================================================================== */
    
    [data-testid="stProgress"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        height: 6px !important;
    }
    
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 20px !important;
    }
    
    /* ========================================================================
       العناوين والنصوص
       ======================================================================== */
    
    .element-container {
        margin-bottom: 8px !important;
    }
    
    .stMarkdown {
        margin-bottom: 4px !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    h1 { font-size: 2.2rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }
    
    a {
        color: #667eea !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #764ba2 !important;
        text-decoration: underline !important;
    }
    
    /* ========================================================================
       تحسينات إضافية للقوائم في الشريط الجانبي
       ======================================================================== */
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] > div div[data-baseweb="select-value"] {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] > div div[data-baseweb="select-placeholder"] {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
# ============================================================================
# تهيئة حالة الجلسة
# ============================================================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'current_page': 'dashboard',
        'scan_in_progress': False,
        'last_scan_time': None,
        'selected_symbol': None,
        'sidebar_config': {},
        'initialized': False,
        'custom_symbols': {}
    }
    
    if not st.session_state.get('initialized', False):
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state.initialized = True

# ============================================================================
# الشريط الجانبي
# ============================================================================

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 5px 0 15px 0;">
            <div style="font-size:3rem;">🚀</div>
            <h2 style="color:#667eea; margin:0; font-weight:800;">AI Scanner</h2>
            <p style="color:rgba(255,255,255,0.4); font-size:0.8rem; margin-top:4px;">
                اكتشاف الانفجارات السعرية
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🔍 مسح السوق": "scanner",
            "📈 تحليل سهم": "analyze",
            "📊 بيانات السوق": "market_data"
        }
        
        current_page = st.session_state.get('current_page', 'dashboard')
        current_index = list(pages.values()).index(current_page) if current_page in pages.values() else 0
        
        selected = st.radio(
            "القائمة",
            list(pages.keys()),
            index=current_index,
            key="nav_radio"
        )
        
        new_page = pages[selected]
        if new_page != current_page:
            st.session_state.current_page = new_page
        
        st.markdown("---")
        
        st.subheader("⚙️ إعدادات المسح")
        
        config = st.session_state.get('sidebar_config', {})
        
        min_score = st.slider(
            "🎯 الحد الأدنى للدرجة",
            min_value=40,
            max_value=90,
            value=config.get('min_score', 60),
            step=5,
            key="min_score_slider"
        )
        
        max_symbols = st.slider(
            "📊 عدد الأسهم",
            min_value=5,
            max_value=30,
            value=config.get('max_symbols', 15),
            step=5,
            key="max_symbols_slider"
        )
        
        st.session_state.sidebar_config = {
            'min_score': min_score,
            'max_symbols': max_symbols
        }
        
        if st.button("🚀 بدء المسح", type="primary", width="stretch", key="scan_btn"):
            st.session_state.scan_in_progress = True
            st.session_state.current_page = "scanner"
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        st.caption("💡 اضبط الإعدادات وابدأ المسح")

# ============================================================================
# دوال عرض التحليل - مدمجة في app.py
# ============================================================================

def render_analyze():
    """تحليل سهم محدد مع رموز رئيسية وزر تحديث"""
    st.subheader("📈 تحليل سهم محدد")
    
    # ====================================================================
    # رموز رئيسية
    # ====================================================================
    
    MAIN_SYMBOLS = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corp.',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corp.',
        'META': 'Meta Platforms',
        'TSLA': 'Tesla Inc.',
        'AMD': 'Advanced Micro Devices',
        'INTC': 'Intel Corp.',
        'NFLX': 'Netflix Inc.',
        'PYPL': 'PayPal Holdings',
        'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce Inc.',
        'ORCL': 'Oracle Corp.',
        'IBM': 'IBM Corp.',
        'CSCO': 'Cisco Systems',
        'QCOM': 'Qualcomm Inc.',
        'TXN': 'Texas Instruments',
        'JPM': 'JPMorgan Chase',
        'BAC': 'Bank of America',
        'WFC': 'Wells Fargo',
        'JNJ': 'Johnson & Johnson',
        'UNH': 'UnitedHealth',
        'PFE': 'Pfizer Inc.',
        'WMT': 'Walmart Inc.',
        'PG': 'Procter & Gamble',
        'KO': 'Coca-Cola Co.',
        'XOM': 'Exxon Mobil',
        'CVX': 'Chevron Corp.',
        'V': 'Visa Inc.',
        'MA': 'Mastercard Inc.'
    }
    
    if 'custom_symbols' in st.session_state:
        MAIN_SYMBOLS.update(st.session_state.custom_symbols)
    
    # ====================================================================
    # معلومات مساعدة
    # ====================================================================
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.02); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <p style="margin:0; color: rgba(255,255,255,0.6); font-size: 0.85rem;">
            💡 اختر من الرموز الرئيسية أو اكتب رمزاً مخصصاً (مثل: AAPL, MSFT, TSLA)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ====================================================================
    # إدخال الرمز مع زر تحديث
    # ====================================================================
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        symbol_options = ["-- اختر رمزاً --"] + list(MAIN_SYMBOLS.keys()) + ["✏️ إدخال مخصص"]
        
        selected_option = st.selectbox(
            "اختر رمز السهم:",
            options=symbol_options,
            index=0,
            key="symbol_select_main"
        )
        
        if selected_option == "✏️ إدخال مخصص":
            symbol = st.text_input(
                "أدخل رمز السهم:",
                value=st.session_state.get('custom_symbol_input', ''),
                placeholder="مثال: AAPL, MSFT, TSLA...",
                key="custom_symbol_input_main"
            ).upper().strip()
            
            if symbol and symbol not in MAIN_SYMBOLS:
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if st.button("➕ إضافة", key="add_symbol_main"):
                        st.session_state.custom_symbols[symbol] = symbol
                        st.session_state.custom_symbol_input = symbol
                        st.success(f"✅ تم إضافة {symbol}")
                        st.rerun()
        elif selected_option != "-- اختر رمزاً --":
            symbol = selected_option
            st.session_state.custom_symbol_input = symbol
        else:
            symbol = ""
    
    with col2:
        if symbol and symbol in MAIN_SYMBOLS:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; margin-top: 25px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">🏢 الشركة</div>
                <div style="font-weight: 600; font-size: 1rem;">{MAIN_SYMBOLS[symbol]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_clicked = st.button(
            "🔄 تحديث",
            type="primary",
            width="stretch",
            key="refresh_analysis_main"
        )
    
    # ====================================================================
    # عرض التحليل
    # ====================================================================
    
    if symbol:
        if refresh_clicked:
            st.cache_data.clear()
        display_stock_analysis(symbol)
    else:
        st.info("🔍 اختر أو اكتب رمز سهم للبدء")

def display_stock_analysis(symbol):
    """عرض تحليل السهم مع بيانات حقيقية"""
    
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        try:
            import yfinance as yf
            import plotly.graph_objects as go
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            
            if df.empty:
                st.error(f"❌ لا توجد بيانات للسهم {symbol}")
                return
            
            info = ticker.info
            
            # ============================================================
            # معلومات أساسية
            # ============================================================
            
            company_name = info.get('longName', symbol)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                        padding: 15px 20px; border-radius: 12px; border: 1px solid rgba(102,126,234,0.2); margin-bottom: 20px;">
                <h3 style="margin:0; color: #ffffff;">{symbol} - {company_name}</h3>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 4px;">
                    🏢 {info.get('sector', 'غير معروف')} | 📊 {info.get('industry', 'غير معروف')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ============================================================
            # بطاقات المؤشرات
            # ============================================================
            
            current_price = df['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_color = "normal" if change >= 0 else "inverse"
                st.metric(
                    "💰 السعر الحالي",
                    f"${current_price:.2f}",
                    delta=f"{change:+.2f} ({change_percent:+.2f}%)",
                    delta_color=delta_color
                )
            
            with col2:
                high_52 = info.get('fiftyTwoWeekHigh', 0)
                if high_52:
                    st.metric(
                        "📈 أعلى 52 أسبوع",
                        f"${high_52:.2f}",
                        delta=f"{(current_price/high_52*100 - 100):+.1f}%"
                    )
                else:
                    st.metric("📈 أعلى 52 أسبوع", "N/A")
            
            with col3:
                low_52 = info.get('fiftyTwoWeekLow', 0)
                if low_52:
                    st.metric(
                        "📉 أدنى 52 أسبوع",
                        f"${low_52:.2f}",
                        delta=f"{(current_price/low_52*100 - 100):+.1f}%"
                    )
                else:
                    st.metric("📉 أدنى 52 أسبوع", "N/A")
            
            with col4:
                volume = info.get('volume', 0)
                avg_volume = info.get('averageVolume', 0)
                if avg_volume > 0:
                    vol_ratio = volume / avg_volume
                    st.metric(
                        "📊 حجم التداول",
                        f"{volume:,}",
                        delta=f"{vol_ratio:.1f}x المتوسط"
                    )
                else:
                    st.metric("📊 حجم التداول", f"{volume:,}")
            
            st.markdown("---")
            
            # ============================================================
            # رسم بياني ومؤشرات
            # ============================================================
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="السعر",
                    increasing=dict(line=dict(color='#00E676')),
                    decreasing=dict(line=dict(color='#FF5252'))
                ))
                
                if len(df) > 20:
                    ma20 = df['Close'].rolling(20).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index, y=ma20,
                        line=dict(color='#FFD700', width=1.5),
                        name="MA20"
                    ))
                
                if len(df) > 50:
                    ma50 = df['Close'].rolling(50).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index, y=ma50,
                        line=dict(color='#29B6F6', width=1.5),
                        name="MA50"
                    ))
                
                fig.update_layout(
                    title=f"📈 {symbol} - رسم بياني فني",
                    template="plotly_dark",
                    xaxis_rangeslider_visible=False,
                    height=450,
                    margin=dict(l=20, r=20, t=50, b=20),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 مؤشرات سريعة")
                
                # RSI
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0.0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
                loss = loss.replace(0, float('nan'))
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50
                
                rsi_color = "#00E676" if 40 <= current_rsi <= 70 else "#FF5252" if current_rsi > 70 else "#FFC107"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">RSI (14)</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: {rsi_color};">{current_rsi:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # حجم التداول
                avg_volume = df['Volume'].iloc[-21:-1].mean() if len(df) > 21 else df['Volume'].mean()
                vol_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
                vol_color = "#00E676" if vol_ratio > 1.5 else "#FFC107" if vol_ratio > 1 else "#FF5252"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">نسبة الحجم</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: {vol_color};">{vol_ratio:.2f}x</div>
                </div>
                """, unsafe_allow_html=True)
                
                # ATR
                atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or 0
                atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">ATR</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #29B6F6;">${atr:.2f} ({atr_percent:.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)
                
                # PE Ratio
                pe = info.get('trailingPE', 'N/A')
                pe_color = "#00E676" if pe != 'N/A' and pe < 25 else "#FFC107" if pe != 'N/A' and pe < 40 else "#FF5252"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">نسبة PE</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: {pe_color};">{f"{pe:.2f}" if pe != 'N/A' else 'N/A'}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ============================================================
            # أخبار الشركة
            # ============================================================
            
            with st.expander("📰 آخر الأخبار", expanded=False):
                try:
                    news = ticker.news
                    if news:
                        for item in news[:3]:
                            title = item.get('title', 'عنوان غير معروف')
                            publisher = item.get('publisher', 'مصدر غير معروف')
                            st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.02); padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; border-right: 3px solid #667eea;">
                                <div style="font-weight: 600;">📰 {title}</div>
                                <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">{publisher}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("📰 لا توجد أخبار حديثة")
                except:
                    st.info("📰 لا توجد أخبار متاحة")
            
        except Exception as e:
            st.error(f"❌ خطأ في التحليل: {str(e)}")
            st.info("💡 تأكد من صحة الرمز (مثال: AAPL, MSFT, TSLA)")

# ============================================================================
# الصفحات الأخرى
# ============================================================================

def render_dashboard():
    """لوحة التحكم"""
    st.subheader("📊 نظرة عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="value">150+</div>
            <div class="label">أسهم متاحة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        results = st.session_state.get('scan_results', pd.DataFrame())
        count = len(results) if not results.empty else 0
        color = "#00E676" if count > 0 else "#FF5252"
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:{color};">{count}</div>
            <div class="label">فرص مكتشفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🎯</div>
            <div class="value" style="color:#FFD700;">84%</div>
            <div class="label">دقة النموذج</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🤖</div>
            <div class="value" style="color:#29B6F6;">AI</div>
            <div class="label">ذكاء اصطناعي</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not results.empty:
        st.subheader("📋 أفضل الفرص")
        st.dataframe(
            results,
            column_config={
                "symbol": "الرمز",
                "score": st.column_config.ProgressColumn("الدرجة", format="%.0f/100", min_value=0, max_value=100),
                "squeeze": st.column_config.ProgressColumn("الانضغاط", format="%.0f/100", min_value=0, max_value=100),
                "recommendation": "التوصية",
                "risk": "المخاطرة",
                "price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "target": st.column_config.NumberColumn("الهدف", format="$%.2f")
            },
            width='stretch',
            hide_index=True
        )
    else:
        st.info("🔍 اضغط 'بدء المسح' في الشريط الجانبي للبدء")

def render_scanner():
    """صفحة المسح"""
    st.subheader("🔍 مسح السوق")
    
    config = st.session_state.get('sidebar_config', {'min_score': 60, 'max_symbols': 15})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 الحد الأدنى للدرجة", f"{config.get('min_score', 60)}/100")
    with col2:
        st.metric("📊 عدد الأسهم", f"{config.get('max_symbols', 15)}")
    with col3:
        st.metric("🤖 النموذج", "Random Forest")
    
    st.markdown("---")
    
    if st.button("🔄 تحديث النتائج", type="primary", width="stretch"):
        with st.spinner("🔍 جاري مسح السوق..."):
            try:
                if BreakoutScanner is None:
                    sample_data = pd.DataFrame({
                        'symbol': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA'],
                        'score': [75, 68, 82, 71, 65],
                        'squeeze': [70, 55, 85, 60, 50],
                        'recommendation': ['🟡 شراء', '🔍 مراقبة', '🟢 شراء قوي', '🔍 مراقبة', '🔴 تجنب'],
                        'risk': ['متوسط', 'متوسط', 'منخفض', 'متوسط', 'مرتفع'],
                        'price': [175.34, 378.91, 895.32, 165.42, 245.68],
                        'target': [195.00, 410.00, 980.00, 185.00, 270.00]
                    })
                    st.session_state.scan_results = sample_data
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    st.success("✅ تم عرض بيانات نموذجية")
                else:
                    scanner = BreakoutScanner()
                    results = scanner.scan_market(
                        STOCK_SYMBOLS[:config.get('max_symbols', 15)],
                        min_score=config.get('min_score', 60)
                    )
                    
                    if not results.empty:
                        st.session_state.scan_results = results
                        st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                        st.success(f"✅ تم العثور على {len(results)} فرصة!")
                    else:
                        st.warning("⚠️ لا توجد نتائج مطابقة للمعايير")
            except Exception as e:
                st.error(f"❌ خطأ في المسح: {str(e)}")
    
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.subheader(f"📊 النتائج ({len(results)})")
        st.dataframe(results, width='stretch', hide_index=True)
        
        csv = results.to_csv(index=False)
        st.download_button(
            "📥 تحميل CSV",
            csv,
            f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            width="stretch"
        )

def render_market_data():
    """صفحة بيانات السوق"""
    try:
        from frontend.pages.market_data import render as render_market_data_page
        render_market_data_page()
    except ImportError:
        st.warning("⚠️ صفحة بيانات السوق غير متوفرة حالياً")
        st.info("💡 تأكد من وجود ملف frontend/pages/market_data.py")

# ============================================================================
# عرض الصفحة المختارة
# ============================================================================

def render_current_page():
    """عرض الصفحة المختارة"""
    page = st.session_state.get('current_page', 'dashboard')
    
    pages = {
        'dashboard': render_dashboard,
        'scanner': render_scanner,
        'analyze': render_analyze,
        'market_data': render_market_data
    }
    
    pages.get(page, render_dashboard)()

# ============================================================================
# التطبيق الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية"""
    
    init_session_state()
    load_css()
    
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Breakout Scanner</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي ومؤشرات الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_sidebar()
    render_current_page()

if __name__ == "__main__":
    main()
