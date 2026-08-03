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
import json
import pickle

def save_results_to_file(results: pd.DataFrame, filename: str = "scan_results.pkl"):
    """حفظ نتائج المسح في ملف"""
    try:
        results.to_pickle(filename)
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ النتائج: {e}")
        return False

def load_results_from_file(filename: str = "scan_results.pkl") -> pd.DataFrame:
    """تحميل نتائج المسح من ملف"""
    try:
        if os.path.exists(filename):
            return pd.read_pickle(filename)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في تحميل النتائج: {e}")
        return pd.DataFrame()
warnings.filterwarnings('ignore')

# ============================================================================
# 1. إعدادات الصفحة الأساسية
# ============================================================================

st.set_page_config(
    page_title="AI Breakout Scanner | ماسح الانفجار السعري",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المسارات المباشرة للمشروع
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# 2. استيراد المكونات والإعدادات
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
# 3. تحميل التصميم والاستايل (CSS)
# ============================================================================

def load_inline_css():
    """استايل مضمن بديل بفكرة Dark Mode فائقة الوضوح"""
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
    
    /* ===== الجداول ===== */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }
    
    /* ===== القوائم المنسدلة ===== */
    div[data-baseweb="select"] > div {
        background-color: #1e1e38 !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] * {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def load_css():
    """تحميل ملف الاستايل الخارجي أو المضمن"""
    css_path = os.path.join(ROOT_DIR, "frontend", "assets", "style.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        except Exception:
            load_inline_css()
    else:
        load_inline_css()

# ============================================================================
# 4. تهيئة حالة الجلسة (Session State)
# ============================================================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة لمكافحة عدم استجابة الأزرار"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'current_page': 'dashboard',
        'scan_in_progress': False,
        'last_scan_time': None,
        'selected_symbol': 'AAPL',
        'sidebar_config': {
            'sector': 'الكل',
            'min_score': 60,
            'max_symbols': 15
        },
        'initialized': True,
        'custom_symbols': {},
        'custom_symbol_input': ''
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# 5. دوال مساعدة للبيانات والقطاعات
# ============================================================================

def get_symbols_by_sector(sector):
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
    if isinstance(STOCK_SYMBOLS, dict):
        return ['الكل'] + [s for s in STOCK_SYMBOLS.keys() if s != 'الكل']
    return ['الكل']

# ============================================================================
# 6. الشريط الجانبي (Sidebar)
# ============================================================================

def render_sidebar():
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
        
        # القائمة الرئيسية
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
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.rerun()
        
        st.markdown("---")
        st.subheader("⚙️ إعدادات المسح")
        
        config = st.session_state.get('sidebar_config', {})
        sectors = get_sectors()
        current_sector = config.get('sector', 'الكل')
        sector_index = sectors.index(current_sector) if current_sector in sectors else 0
        
        sector = st.selectbox("🏢 القطاع", sectors, index=sector_index, key="sector_select")
        min_score = st.slider("🎯 الحد الأدنى للدرجة", 40, 90, config.get('min_score', 60), 5, key="min_score_slider")
        max_symbols = st.slider("📊 عدد الأسهم", 5, 30, config.get('max_symbols', 15), 5, key="max_symbols_slider")
        
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
# 7. الصفحات المختلفة (Render Pages)
# ============================================================================

def render_dashboard():
    st.subheader("📊 نظرة عامة")
    
    # الحصول على البيانات من session state
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    col1, col2, col3, col4 = st.columns(4)
    
    # عدد الأسهم المتاحة
    all_symbols = []
    if isinstance(STOCK_SYMBOLS, dict):
        for syms in STOCK_SYMBOLS.values():
            if isinstance(syms, list):
                all_symbols.extend(syms)
    total_stocks = len(set(all_symbols))
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="value">{total_stocks}</div>
            <div class="label">أسهم متاحة</div>
        </div>
        """, unsafe_allow_html=True)
    
    # عدد الفرص المكتشفة
    opportunities = len(results) if not results.empty else 0
    color = "#00E676" if opportunities > 0 else "#FF5252"
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:{color};">{opportunities}</div>
            <div class="label">فرص مكتشفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    # متوسط درجة الثقة
    avg_score = results['Score'].mean() if not results.empty and 'Score' in results.columns else 0
    avg_score = round(avg_score, 1) if not pd.isna(avg_score) else 0
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🎯</div>
            <div class="value" style="color:#FFD700;">{avg_score}%</div>
            <div class="label">متوسط الثقة</div>
        </div>
        """, unsafe_allow_html=True)
    
    # وقت آخر مسح
    last_scan = st.session_state.get('last_scan_time', 'لم يتم')
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">⏱️</div>
            <div class="value" style="font-size:1.2rem; color:#29B6F6;">{last_scan}</div>
            <div class="label">آخر تحديث</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # عرض أفضل الفرص
    if not results.empty:
        st.subheader("🏆 أفضل الفرص المكتشفة")
        
        # ترتيب حسب الدرجة
        if 'Score' in results.columns:
            top_results = results.sort_values('Score', ascending=False).head(10)
        else:
            top_results = results.head(10)
        
        st.dataframe(top_results, use_container_width=True)
        
        # عرض رسم بياني بسيط للدرجات
        if 'Score' in results.columns and len(results) > 1:
            st.subheader("📊 توزيع درجات الثقة")
            chart_data = results[['Symbol', 'Score']].set_index('Symbol')
            st.bar_chart(chart_data)
    else:
        st.info("💡 لم يتم إجراء مسح بعد. استخدم الشريط الجانبي لبدء تحليل السوق.")

def render_scanner():
    st.subheader("🔍 مسح السوق لتتبع الانفجارات السعرية")
    
    # زر المسح مع حالة التقدم
    col1, col2 = st.columns([1, 3])
    with col1:
        scan_clicked = st.button("🚀 بدء المسح الآن", type="primary", use_container_width=True)
    
    with col2:
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
    
    if scan_clicked or st.session_state.get('scan_in_progress', False):
        if scan_clicked:
            st.session_state.scan_in_progress = True
        
        with st.spinner("🔍 جاري مسح السوق وتحليل الأسهم..."):
            # محاكاة المسح
            import time
            progress_bar = st.progress(0)
            
            # محاكاة تقدم المسح
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            # إنشاء نتائج وهمية للعرض
            import random
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD']
            results = []
            for sym in random.sample(symbols, min(len(symbols), 5)):
                results.append({
                    'Symbol': sym,
                    'Price': round(random.uniform(100, 500), 2),
                    'Score': random.randint(65, 95),
                    'Signal': random.choice(['🚀 BUY', '📊 HOLD', '⚠️ SELL']),
                    'Volume': random.choice(['مرتفع', 'متوسط', 'منخفض']),
                    'Pattern': random.choice(['اختراق', 'انعكاس', 'استمرار'])
                })
            
            df_results = pd.DataFrame(results)
            st.session_state.scan_results = df_results
            st.session_state.scan_in_progress = False
            st.session_state.last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            st.success(f"✅ اكتمل المسح! تم العثور على {len(results)} فرصة.")
    
    # عرض النتائج
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.subheader("📊 نتائج المسح")
        st.dataframe(results, use_container_width=True)
        
        # إضافة زر لتصدير النتائج
        csv = results.to_csv(index=False)
        st.download_button(
            label="📥 تحميل النتائج (CSV)",
            data=csv,
            file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("💡 اضغط على 'بدء المسح الآن' لبدء تحليل السوق.")

def render_analyze():
    st.subheader("📈 تحليل سهم محدد")
    
    # ----- الحل الآمن لمشكلة AttributeError -----
    # الحصول على القيمة الافتراضية مع التأكد من أنها ليست None
    default_value = st.session_state.get('selected_symbol')
    if default_value is None or default_value == '':
        default_value = 'AAPL'
    
    # عرض مربع الإدخال مع القيمة الافتراضية الآمنة
    symbol = st.text_input(
        "أدخل رمز السهم:",
        value=default_value,
        placeholder="مثال: AAPL, TSLA, NVDA"
    ).upper()
    
    # ----- تحسينات إضافية -----
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_clicked = st.button("🔍 تحليل الآن", type="primary", use_container_width=True)
    
    with col2:
        # عرض آخر رمز تم تحليله
        if 'last_analyzed' in st.session_state:
            st.caption(f"آخر تحليل: {st.session_state.last_analyzed}")
    
    if analyze_clicked:
        if not symbol.strip():
            st.warning("⚠️ الرجاء إدخال رمز سهم صحيح")
            return
            
        st.session_state.selected_symbol = symbol
        st.session_state.last_analyzed = symbol
        
        with st.spinner(f"جاري تحليل {symbol}..."):
            # محاكاة التحليل (يجب استبدالها بالدالة الحقيقية)
            import time
            time.sleep(1)
            
            # عرض بيانات التحليل
            st.success(f"✅ تم تحليل السهم {symbol} بنجاح!")
            
            # عرض معلومات وهمية للتوضيح
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("السعر الحالي", "$178.50", "+2.3%")
            with col2:
                st.metric("RSI", "58.4", "محايد")
            with col3:
                st.metric("الإشارة", "🚀 شراء", "قوية")
            
            # عرض تفاصيل إضافية
            with st.expander("📊 تفاصيل المؤشرات الفنية", expanded=True):
                st.json({
                    "Symbol": symbol,
                    "RSI": 58.4,
                    "MACD": "إيجابي",
                    "Bollinger Bands": "ضيق (Squeeze)",
                    "Volume": "متوسط",
                    "Signal": "BUY",
                    "Confidence": "85%"
                })
            
            # حفظ النتيجة في session state للاستخدام في صفحات أخرى
            st.session_state.analysis_result = {
                'symbol': symbol,
                'rsi': 58.4,
                'signal': 'BUY',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

def render_market_data():
    st.subheader("📊 بيانات السوق اليومية")
    
    # عرض مؤشرات السوق الرئيسية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("S&P 500", "4,543.20", "+0.85%")
    with col2:
        st.metric("NASDAQ", "14,234.50", "+1.12%")
    with col3:
        st.metric("DOW", "34,567.80", "+0.65%")
    
    st.markdown("---")
    
    # عرض الأسهم القيادية
    st.subheader("🏢 الأسهم القيادية")
    
    # عرض نتائج المسح إن وجدت
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.info("لا توجد بيانات حالية. قم بتشغيل المسح من الشريط الجانبي.")

# ============================================================================
# 8. التشغيل الرئيسي والتوجيه (Main Router)
# ============================================================================

def main():
    # تحميل التنسيقات
    load_css()
    
    # تهيئة حالات الجلسة
    init_session_state()
    
    # عرض الشريط الجانبي
    render_sidebar()
    
    # توجيه الصفحات حسب الصفحة الحالية
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'scanner':
        render_scanner()
    elif page == 'analyze':
        render_analyze()
    elif page == 'market_data':
        render_market_data()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
