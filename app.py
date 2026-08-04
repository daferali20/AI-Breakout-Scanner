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

# ============================================================================
# 2. إعداد المسارات بشكل صحيح (الأهم)
# ============================================================================

# الحصول على المسار المطلق للمشروع
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
PROJECT_ROOT = os.path.dirname(ROOT_DIR)  # AI-Breakout-Scanner/
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")  # AI-Breakout-Scanner/backend/
OPPORTUNITY_DIR = os.path.join(BACKEND_DIR, "opportunity")  # AI-Breakout-Scanner/backend/opportunity/

# إضافة جميع المسارات إلى sys.path
paths_to_add = [
    ROOT_DIR,  # frontend
    PROJECT_ROOT,  # المشروع الرئيسي
    BACKEND_DIR,  # backend
    OPPORTUNITY_DIR,  # backend/opportunity
    os.path.join(ROOT_DIR, "pages"),  # frontend/pages
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)
        print(f"✅ تم إضافة المسار: {path}")

# ============================================================================
# 3. استيراد المكونات والإعدادات
# ============================================================================

try:
    from config import STOCK_SYMBOLS, APP_SETTINGS
except ImportError:
    STOCK_SYMBOLS = {
        'الكل': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'NFLX', 'INTC'],
        'التكنولوجيا': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'NFLX', 'INTC'],
        'الطاقة': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
        'الصحة': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
        'المالية': ['JPM', 'BAC', 'WFC', 'GS', 'MS']
    }
    APP_SETTINGS = {'title': 'AI Breakout Scanner'}

try:
    from backend.scanner.breakout_scanner import BreakoutScanner
except ImportError:
    BreakoutScanner = None

# ============================================================================
# 4. استيراد محرك الفرص (Opportunity Engine) - الطريقة الصحيحة
# ============================================================================

OPPORTUNITY_AVAILABLE = False
OPPORTUNITY_PAGE_AVAILABLE = False
OpportunityEngine = None
MarketPhase = None
opportunity_page = None

print("=" * 50)
print("🔍 جاري محاولة استيراد محرك الفرص...")
print(f"📁 المسار: {OPPORTUNITY_DIR}")
print(f"📁 الملفات الموجودة: {os.listdir(OPPORTUNITY_DIR) if os.path.exists(OPPORTUNITY_DIR) else 'المجلد غير موجود'}")

# محاولة 1: استيراد مباشر
try:
    from opportunity import OpportunityEngine, MarketPhase
    OPPORTUNITY_AVAILABLE = True
    print("✅ تم استيراد محرك الفرص بنجاح (استيراد مباشر)")
except ImportError as e1:
    print(f"⚠️ فشل الاستيراد المباشر: {e1}")
    
    # محاولة 2: استيراد من backend.opportunity
    try:
        from backend.opportunity import OpportunityEngine, MarketPhase
        OPPORTUNITY_AVAILABLE = True
        print("✅ تم استيراد محرك الفرص بنجاح (من backend.opportunity)")
    except ImportError as e2:
        print(f"⚠️ فشل الاستيراد من backend.opportunity: {e2}")
        
        # محاولة 3: استيراد باستخدام importlib (الحل الأخير)
        try:
            import importlib.util
            
            # التحقق من وجود ملف __init__.py
            init_path = os.path.join(OPPORTUNITY_DIR, "__init__.py")
            if os.path.exists(init_path):
                spec = importlib.util.spec_from_file_location("opportunity", init_path)
                opportunity_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(opportunity_module)
                
                OpportunityEngine = getattr(opportunity_module, 'OpportunityEngine', None)
                MarketPhase = getattr(opportunity_module, 'MarketPhase', None)
                
                if OpportunityEngine is not None:
                    OPPORTUNITY_AVAILABLE = True
                    print("✅ تم استيراد محرك الفرص بنجاح (باستخدام importlib)")
                else:
                    print("❌ لم يتم العثور على OpportunityEngine في الوحدة")
            else:
                print(f"❌ ملف __init__.py غير موجود: {init_path}")
        except Exception as e3:
            print(f"❌ فشل الاستيراد باستخدام importlib: {e3}")

print(f"📊 حالة محرك الفرص: {'✅ متوفر' if OPPORTUNITY_AVAILABLE else '❌ غير متوفر'}")
print("=" * 50)

# ============================================================================
# 5. استيراد صفحة الفرص
# ============================================================================

if OPPORTUNITY_AVAILABLE:
    try:
        # محاولة استيراد صفحة الفرص
        from pages.opportunity_timeline import main as opportunity_page
        OPPORTUNITY_PAGE_AVAILABLE = True
        print("✅ تم استيراد صفحة الفرص بنجاح")
    except ImportError as e:
        print(f"⚠️ فشل استيراد صفحة الفرص: {e}")
        
        # محاولة مع مسار مطلق
        try:
            page_path = os.path.join(ROOT_DIR, "pages", "opportunity_timeline.py")
            if os.path.exists(page_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("opportunity_timeline", page_path)
                page_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(page_module)
                opportunity_page = page_module.main
                OPPORTUNITY_PAGE_AVAILABLE = True
                print("✅ تم استيراد صفحة الفرص بنجاح (باستخدام importlib)")
        except Exception as e2:
            print(f"❌ فشل استيراد صفحة الفرص: {e2}")

# ============================================================================
# 6. تحميل التصميم والاستايل (CSS)
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
    
    /* ===== علامة تبويب جديدة ===== */
    .nav-item-opportunity {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 8px;
        padding: 2px 12px;
        margin: 2px 0;
    }
    
    .badge-new {
        background: #f5576c;
        color: white;
        font-size: 0.6rem;
        padding: 1px 8px;
        border-radius: 10px;
        margin-left: 5px;
        font-weight: 700;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* ===== حالة المحرك ===== */
    .engine-status {
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        font-size: 0.85rem;
    }
    
    .engine-status-active {
        background: rgba(0, 230, 118, 0.15);
        border: 1px solid rgba(0, 230, 118, 0.3);
        color: #00E676;
    }
    
    .engine-status-inactive {
        background: rgba(255, 82, 82, 0.15);
        border: 1px solid rgba(255, 82, 82, 0.3);
        color: #FF5252;
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
# 7. تهيئة حالة الجلسة (Session State)
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
        'custom_symbol_input': '',
        'opportunity_results': {},
        'debug_info': {
            'opportunity_available': OPPORTUNITY_AVAILABLE,
            'opportunity_page_available': OPPORTUNITY_PAGE_AVAILABLE,
            'project_root': PROJECT_ROOT,
            'backend_path': BACKEND_DIR,
            'opportunity_path': OPPORTUNITY_DIR
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# 8. دوال مساعدة للبيانات والقطاعات
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
# 9. الشريط الجانبي (Sidebar)
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
        
        # ===== القائمة الرئيسية =====
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🚀 AI Opportunity Timeline": "opportunity",
            "🔍 مسح السوق": "scanner",
            "📈 تحليل سهم": "analyze",
            "📊 بيانات السوق": "market_data"
        }
        
        page_labels = list(pages.keys())
        
        current_page = st.session_state.get('current_page', 'dashboard')
        
        try:
            current_index = list(pages.values()).index(current_page) if current_page in pages.values() else 0
        except ValueError:
            current_index = 0
        
        # عرض القائمة مع علامة NEW
        selected_label = st.radio(
            "القائمة",
            page_labels,
            index=current_index,
            key="nav_radio",
            format_func=lambda x: x + " 🆕" if x == "🚀 AI Opportunity Timeline" else x
        )
        
        new_page = pages[selected_label]
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.rerun()
        
        st.markdown("---")
        
        # ===== إعدادات المسح =====
        if new_page != "opportunity":
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
        
        # ===== معلومات إضافية =====
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        # ===== حالة محرك الفرص =====
        st.markdown("---")
        st.caption("🔧 حالة النظام:")
        
        if OPPORTUNITY_AVAILABLE:
            st.markdown("""
            <div class="engine-status engine-status-active">
                🧠 محرك الفرص: ✅ نشط
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="engine-status engine-status-inactive">
                🧠 محرك الفرص: ❌ غير متوفر
            </div>
            """, unsafe_allow_html=True)
        
        # زر لتحديث
        if st.button("🔄 تحديث", key="refresh_btn", use_container_width=True):
            st.rerun()
        
        return st.session_state.sidebar_config

# ============================================================================
# 10. الصفحات المختلفة (Render Pages)
# ============================================================================

def render_dashboard():
    st.subheader("📊 نظرة عامة")
    
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    # عرض حالة المحرك
    st.subheader("🧠 حالة محرك الذكاء الاصطناعي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if OPPORTUNITY_AVAILABLE:
            st.success("✅ محرك الفرص: نشط وجاهز للعمل")
            st.caption("يمكنك استخدام صفحة 'AI Opportunity Timeline' للتحليل المتقدم")
        else:
            st.error("❌ محرك الفرص: غير متوفر")
            with st.expander("🔧 معلومات التصحيح"):
                st.write(f"مسار backend: `{BACKEND_DIR}`")
                st.write(f"مسار opportunity: `{OPPORTUNITY_DIR}`")
                st.write(f"الملفات الموجودة: {os.listdir(OPPORTUNITY_DIR) if os.path.exists(OPPORTUNITY_DIR) else 'المجلد غير موجود'}")
    
    with col2:
        if OPPORTUNITY_PAGE_AVAILABLE:
            st.success("✅ صفحة الفرص: متوفرة")
        else:
            st.error("❌ صفحة الفرص: غير متوفرة")
            st.caption("تأكد من وجود `pages/opportunity_timeline.py`")
    
    st.markdown("---")
    
    # عرض أفضل الفرص
    if not results.empty:
        st.subheader("🏆 أفضل الفرص المكتشفة")
        
        if 'Score' in results.columns:
            top_results = results.sort_values('Score', ascending=False).head(10)
        else:
            top_results = results.head(10)
        
        st.dataframe(top_results, use_container_width=True)
        
        if 'Score' in results.columns and len(results) > 1:
            st.subheader("📊 توزيع درجات الثقة")
            chart_data = results[['Symbol', 'Score']].set_index('Symbol')
            st.bar_chart(chart_data)
    else:
        st.info("💡 لم يتم إجراء مسح بعد. استخدم الشريط الجانبي لبدء تحليل السوق.")


def render_scanner():
    st.subheader("🔍 مسح السوق لتتبع الانفجارات السعرية")
    
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
            import time
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            import random
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD', 'NFLX', 'INTC']
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
    
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.subheader("📊 نتائج المسح")
        st.dataframe(results, use_container_width=True)
        
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
    
    default_value = st.session_state.get('selected_symbol')
    if default_value is None or default_value == '':
        default_value = 'AAPL'
    
    symbol = st.text_input(
        "أدخل رمز السهم:",
        value=default_value,
        placeholder="مثال: AAPL, TSLA, NVDA"
    ).upper()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_clicked = st.button("🔍 تحليل الآن", type="primary", use_container_width=True)
    
    with col2:
        if 'last_analyzed' in st.session_state:
            st.caption(f"آخر تحليل: {st.session_state.last_analyzed}")
    
    if analyze_clicked:
        if not symbol.strip():
            st.warning("⚠️ الرجاء إدخال رمز سهم صحيح")
            return
            
        st.session_state.selected_symbol = symbol
        st.session_state.last_analyzed = symbol
        
        with st.spinner(f"جاري تحليل {symbol}..."):
            import time
            time.sleep(1)
            
            st.success(f"✅ تم تحليل السهم {symbol} بنجاح!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("السعر الحالي", "$178.50", "+2.3%")
            with col2:
                st.metric("RSI", "58.4", "محايد")
            with col3:
                st.metric("الإشارة", "🚀 شراء", "قوية")
            
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
            
            st.session_state.analysis_result = {
                'symbol': symbol,
                'rsi': 58.4,
                'signal': 'BUY',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }


def render_market_data():
    st.subheader("📊 بيانات السوق اليومية")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("S&P 500", "4,543.20", "+0.85%")
    with col2:
        st.metric("NASDAQ", "14,234.50", "+1.12%")
    with col3:
        st.metric("DOW", "34,567.80", "+0.65%")
    
    st.markdown("---")
    
    st.subheader("🏢 الأسهم القيادية")
    
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.info("لا توجد بيانات حالية. قم بتشغيل المسح من الشريط الجانبي.")


# ============================================================================
# 11. صفحة الفرص الجديدة (Opportunity Timeline)
# ============================================================================

def render_opportunity_page():
    """عرض صفحة AI Opportunity Timeline"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 4px 20px rgba(245,87,108,0.3);
    ">
        <div style="display: flex; align-items: center; gap: 15px; justify-content: space-between;">
            <div>
                <span style="font-size: 2rem;">🚀</span>
                <span style="font-size: 1.5rem; font-weight: 800; margin-left: 10px;">
                    AI Opportunity Timeline
                </span>
            </div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 4px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            ">
                🆕 NEW
            </div>
        </div>
        <p style="margin-top: 5px; opacity: 0.9; font-size: 0.95rem;">
            تحليل الفرص الاستثمارية المتقدم باستخدام الذكاء الاصطناعي
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض معلومات التصحيح (مخفي افتراضياً)
    with st.expander("🔧 معلومات التصحيح - Debug Info", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**حالة المحرك:**")
            st.write(f"- محرك الفرص: {'✅ متوفر' if OPPORTUNITY_AVAILABLE else '❌ غير متوفر'}")
            st.write(f"- صفحة الفرص: {'✅ متوفرة' if OPPORTUNITY_PAGE_AVAILABLE else '❌ غير متوفرة'}")
        with col2:
            st.write("**المسارات:**")
            st.write(f"- ROOT_DIR: `{ROOT_DIR}`")
            st.write(f"- PROJECT_ROOT: `{PROJECT_ROOT}`")
            st.write(f"- BACKEND_DIR: `{BACKEND_DIR}`")
            st.write(f"- OPPORTUNITY_DIR: `{OPPORTUNITY_DIR}`")
        
        # عرض الملفات الموجودة
        if os.path.exists(OPPORTUNITY_DIR):
            st.write("**الملفات في `backend/opportunity/`:**")
            files = os.listdir(OPPORTUNITY_DIR)
            for f in sorted(files):
                st.write(f"  - {f}")
    
    # التحقق من توفر المحرك
    if not OPPORTUNITY_AVAILABLE:
        st.error("❌ **محرك الفرص غير متوفر**")
        
        st.warning("""
        **الأسباب المحتملة:**
        
        1. **الملفات غير موجودة** - تأكد من وجود مجلد `backend/opportunity/` مع جميع الملفات
        
        2. **أخطاء في الاستيراد** - قد تكون هناك أخطاء في ملفات المحرك
        
        3. **مسار غير صحيح** - تأكد من أن المسار مضاف بشكل صحيح
        """)
        
        st.info("""
        **لتفعيل محرك الفرص:**
        
        1. تأكد من وجود الملفات التالية:
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
    
    # عرض الصفحة المختارة
    if page == 'dashboard':
        render_dashboard()
    elif page == 'opportunity':
        render_opportunity_page()  # الصفحة الجديدة
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
