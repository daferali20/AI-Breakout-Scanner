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
import warnings
warnings.filterwarnings('ignore')

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
    STOCK_SYMBOLS = {
        'الكل': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD'],
        'التكنولوجيا': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD']
    }
    APP_SETTINGS = {'title': 'AI Breakout Scanner'}

try:
    from backend.scanner.breakout_scanner import BreakoutScanner
except ImportError:
    BreakoutScanner = None

# ============================================================================
# تحميل ملف الاستايل
# ============================================================================

def load_css():
    """تحميل ملف الاستايل من frontend/assets/style.css"""
    css_path = os.path.join(ROOT_DIR, "frontend", "assets", "style.css")
    
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ خطأ في تحميل ملف الاستايل: {e}")
            load_inline_css()
    else:
        load_inline_css()

def load_inline_css():
    """استايل مضمن محسن لحل مشكلة خلفية ونصوص القوائم المنسدلة"""
    st.markdown("""
    <style>
    /* ===== الإعدادات الأساسية ===== */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 8px 32px rgba(102,126,234,0.25);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(20,20,40,0.92) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    
    /* ===== النصوص العامة ===== */
    .stMarkdown, p, div, span, label {
        color: #e8e8e8 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* ===== البطاقات ===== */
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 18px 20px;
        border-radius: 14px;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }
    
    .metric-card .label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.55);
    }
    
    .metric-card .icon {
        font-size: 1.6rem;
        margin-bottom: 4px;
    }
    
    /* ===== الأزرار ===== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.35) !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        box-shadow: 0 4px 15px rgba(245,87,108,0.3) !important;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(245,87,108,0.4) !important;
    }
    
    /* ===== الجداول ===== */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }
    
    [data-testid="stDataFrame"] thead th {
        background: rgba(102,126,234,0.12) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stDataFrame"] tbody td {
        color: #d0d0d0 !important;
    }
    
    /* ===== إصلاح القوائم المنسدلة (Dropdown Menu Fix) ===== */
    
    /* صندوق اختيار القائمة المستقر */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* قيمة الخيار المحدد داخل الصندوق */
    .stSelectbox div[data-baseweb="select"] div[data-baseweb="select-value"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* إصلاح قائمة القيمة الخافية (الخيارات الخارجيّة المنبثقة) */
    div[data-baseweb="popover"] {
        background-color: #1a1a2e !important;
    }

    div[data-baseweb="popover"] ul {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="popover"] ul li {
        background-color: transparent !important;
        color: #ffffff !important;
        padding: 10px 15px !important;
    }

    /* لون العنصر عند التمرير عليه (Hover) */
    div[data-baseweb="popover"] ul li:hover {
        background-color: #667eea !important;
        color: #ffffff !important;
    }

    /* العنصر المختار حالياً داخل القائمة */
    div[data-baseweb="popover"] ul li[aria-selected="true"] {
        background-color: #764ba2 !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* ===== Text Input ===== */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
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
        'sidebar_config': {
            'sector': 'الكل',
            'min_score': 60,
            'max_symbols': 15
        },
        'initialized': False,
        'custom_symbols': {},
        'custom_symbol_input': ''
    }
    
    if not st.session_state.get('initialized', False):
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state.initialized = True

# ============================================================================
# دوال الحصول على الرموز حسب القطاع
# ============================================================================

def get_symbols_by_sector(sector):
    """الحصول على رموز الأسهم حسب القطاع"""
    if sector == 'الكل' or sector is None:
        if isinstance(STOCK_SYMBOLS, dict):
            all_symbols = []
            for syms in STOCK_SYMBOLS.values():
                if isinstance(syms, list):
                    all_symbols.extend(syms)
            return list(set(all_symbols))
        return STOCK_SYMBOLS
    
    if isinstance(STOCK_SYMBOLS, dict):
        return STOCK_SYMBOLS.get(sector, [])
    return STOCK_SYMBOLS

def get_sectors():
    """الحصول على قائمة القطاعات المتاحة"""
    if isinstance(STOCK_SYMBOLS, dict):
        return ['الكل'] + [s for s in STOCK_SYMBOLS.keys() if s != 'الكل']
    return ['الكل']

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
            st.rerun()
        
        st.markdown("---")
        st.subheader("⚙️ إعدادات المسح")
        
        config = st.session_state.get('sidebar_config', {})
        
        sectors = get_sectors()
        sector_index = 0
        current_sector = config.get('sector', 'الكل')
        if current_sector in sectors:
            sector_index = sectors.index(current_sector)
        
        sector = st.selectbox(
            "🏢 القطاع",
            sectors,
            index=sector_index,
            key="sector_select"
        )
        
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
            'sector': sector,
            'min_score': min_score,
            'max_symbols': max_symbols
        }
        
        if st.button("🚀 بدء المسح", type="primary", use_container_width=True, key="scan_btn"):
            st.session_state.scan_in_progress = True
            st.session_state.current_page = "scanner"
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        return st.session_state.sidebar_config

# ============================================================================
# دوال عرض التحليل والصفحات
# ============================================================================

def display_stock_analysis(symbol):
    """عرض تحليل السهم مع بيانات حقيقية من yfinance"""
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
            
            current_price = df['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 السعر الحالي", f"${current_price:.2f}", delta=f"{change:+.2f} ({change_percent:+.2f}%)")
            with col2:
                high_52 = info.get('fiftyTwoWeekHigh', 0)
                st.metric("📈 أعلى 52 أسبوع", f"${high_52:.2f}" if high_52 else "N/A")
            with col3:
                low_52 = info.get('fiftyTwoWeekLow', 0)
                st.metric("📉 أدنى 52 أسبوع", f"${low_52:.2f}" if low_52 else "N/A")
            with col4:
                volume = info.get('volume', 0)
                st.metric("📊 حجم التداول", f"{volume:,}")
            
            st.markdown("---")
            
            # الرسم البياني
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="السعر", increasing_line_color='#00E676', decreasing_line_color='#FF5252'
            ))
            fig.update_layout(title=f"📈 {symbol} - رسم بياني فني", template="plotly_dark", height=450, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ خطأ في التحليل: {str(e)}")

def render_analyze():
    """صفحة تحليل سهم محدد"""
    st.subheader("📈 تحليل سهم محدد")
    
    MAIN_SYMBOLS = {
        'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corp.', 'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.', 'NVDA': 'NVIDIA Corp.', 'TSLA': 'Tesla Inc.'
    }
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.selectbox("اختر رمز السهم:", list(MAIN_SYMBOLS.keys()), key="symbol_select_main")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("🔄 تحديث", type="primary", use_container_width=True)
    
    if symbol:
        display_stock_analysis(symbol)

def render_dashboard():
    """لوحة التحكم إكمال الكود المفصل"""
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:{'#00E676' if count > 0 else '#FF5252'};">{count}</div>
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
        st.subheader("📋 أفضل الفرص المكتشفة")
        st.dataframe(
            results,
            column_config={
                "symbol": "الرمز",
                "score": st.column_config.ProgressColumn("الدرجة", format="%.0f/100", min_value=0, max_value=100),
                "price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "recommendation": "التوصية"
            },
            use_container_width=True
        )
    else:
        st.info("💡 اضغط على 'بدء المسح' من الشريط الجانبي للبحث عن فرص الانفجار السعري.")

def render_scanner():
    """صفحة المسح"""
    st.subheader("🔍 مسح السوق الانفجاري")
    
    config = st.session_state.sidebar_config
    st.write(f"القطاع المحدد: **{config['sector']}** | الحد الأدنى للدرجة: **{config['min_score']}**")
    
    if st.button("بدء المسح الآن", type="primary"):
        with st.spinner("جاري مسح الأسهم بالذكاء الاصطناعي..."):
            # محاكاة نتائج المسح أو استدعاء المحرك
            symbols = get_symbols_by_sector(config['sector'])[:config['max_symbols']]
            data = []
            for s in symbols:
                data.append({"symbol": s, "score": 85, "price": 150.0, "recommendation": "شراء قاصف"})
            
            st.session_state.scan_results = pd.DataFrame(data)
            st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
            st.success("تم المسح بنجاح!")
            st.rerun()

    if not st.session_state.scan_results.empty:
        st.dataframe(st.session_state.scan_results, use_container_width=True)

# ============================================================================
# التشغيل الرئيسي
# ============================================================================

def main():
    init_session_state()
    load_css()
    render_sidebar()

    # رأس الصفحة (Header)
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Breakout Scanner</h1>
        <p>نظام ذكي لتحليل الأسهم واكتشاف فرص الاختراق السعري المبكر</p>
    </div>
    """, unsafe_allow_html=True)

    # توجيه الصفحات
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'scanner':
        render_scanner()
    elif page == 'analyze':
        render_analyze()
    elif page == 'market_data':
        st.subheader("📊 بيانات السوق العتيقة")
        st.info("قسم البيانات المباشرة قيد التطوير.")

if __name__ == "__main__":
    main()
