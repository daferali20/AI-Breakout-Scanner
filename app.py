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
    
    .stMarkdown, .stText, .stWrite, p, div, span, label {
        color: #e8e8e8 !important;
    }
    
    .stSubheader, .stHeader {
        color: #ffffff !important;
    }
    
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
    
    .stExpander {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stExpander summary {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSlider"] > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSelectbox"] > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    [data-testid="stSelectbox"] label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stAlert {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #e0e0e0 !important;
    }
    
    .stAlert .stMarkdown {
        color: #e0e0e0 !important;
    }
    
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
    
    [data-testid="stProgress"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        height: 6px !important;
    }
    
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 20px !important;
    }
    
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
        'custom_symbols': {}  # لتخزين الرموز المضافة
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
        
        # القائمة
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
        
        # إعدادات المسح
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
# الصفحات
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
                    st.warning("⚠️ ماسح الانفجار غير متوفر، استخدم بيانات نموذجية")
                    # بيانات نموذجية للعرض
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

def render_analyze():
    """تحليل سهم محدد مع رموز رئيسية"""
    st.subheader("📈 تحليل سهم محدد")
    
    # محاولة استيراد صفحة التحليل المتقدمة
    try:
        from frontend.pages.analyze import render as render_analyze_advanced
        render_analyze_advanced()
    except ImportError:
        # النسخة البسيطة إذا لم تتوفر الصفحة المتقدمة
        render_analyze_simple()

def render_analyze_simple():
    """النسخة البسيطة لتحليل السهم"""
    symbol = st.text_input(
        "أدخل رمز السهم",
        value="AAPL",
        key="symbol_input"
    ).upper()
    
    if symbol:
        with st.spinner(f"📊 جاري تحليل {symbol}..."):
            try:
                if BreakoutScanner is None:
                    st.warning("⚠️ ماسح الانفجار غير متوفر")
                    return
                
                scanner = BreakoutScanner()
                result = scanner.scan_stock(symbol)
                
                if 'error' in result:
                    st.error(f"❌ {result['error']}")
                    return
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### 🎯 {symbol}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("الدرجة", f"{result['score']}/100")
                    with col_b:
                        st.metric("التوصية", result['recommendation']['action'])
                    with col_c:
                        st.metric("المخاطرة", result['recommendation']['risk'])
                    
                    st.markdown("---")
                    st.markdown("#### 📍 مستويات التداول")
                    levels = result['levels']
                    st.write(f"💰 السعر الحالي: **${levels['current']:.2f}**")
                    st.write(f"📈 نقطة الدخول: **${levels['entry']:.2f}**")
                    st.write(f"🛑 وقف الخسارة: **${levels['stop_loss']:.2f}**")
                    st.write(f"🎯 الهدف 1: **${levels['target_1']:.2f}**")
                    st.write(f"🎯 الهدف 2: **${levels['target_2']:.2f}**")
                
                with col2:
                    st.markdown("#### 📊 المؤشرات")
                    st.metric("درجة الانضغاط", f"{result['squeeze']['squeeze_score']}/100")
                    st.metric("RSI", f"{result['indicators']['rsi']:.1f}")
                    st.metric("حجم التداول", f"{result['indicators']['volume_ratio']:.2f}x")
                    
                    st.markdown("---")
                    st.markdown("#### 🤖 تنبؤ الذكاء الاصطناعي")
                    ai = result['ai']
                    st.metric("الاحتمالية", f"{ai['probability']}%")
                    st.metric("الثقة", f"{ai['confidence']:.0f}%")
                    
                    if ai['prediction'] == 'explosive':
                        st.success("✅ انفجار متوقع")
                    else:
                        st.warning("⏳ انفجار غير مرجح")
                        
            except Exception as e:
                st.error(f"❌ خطأ في التحليل: {str(e)}")

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
    
    # تهيئة
    init_session_state()
    
    # تحميل التصميم
    load_css()
    
    # الهيدر
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Breakout Scanner</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي ومؤشرات الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # الشريط الجانبي
    render_sidebar()
    
    # الصفحة المختارة
    render_current_page()

if __name__ == "__main__":
    main()
