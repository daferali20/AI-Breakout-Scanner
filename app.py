import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import warnings
import json
from io import BytesIO
import traceback

# قراءة المفتاح
#api_key = st.secrets["OPENAI_API_KEY"]
# أو
#api_key = st.secrets.get("OPENAI_API_KEY", "default_value_if_not_found")

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Breakout Scanner | ماسح الانفجار السعري",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# إعداد المسارات المحسّن
# ============================================================================

def find_project_root():
    """البحث عن جذر المشروع بشكل تلقائي"""
    current = os.path.dirname(os.path.abspath(__file__))
    while current:
        if os.path.exists(os.path.join(current, 'backend')):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # وصلنا إلى الجذر
            break
        current = parent
    return os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = find_project_root()
ROOT_DIR = PROJECT_ROOT

# تحديد مجلد backend المباشر من الجذر
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
OPPORTUNITY_DIR = os.path.join(BACKEND_DIR, "opportunity")
PAGES_DIR = os.path.join(PROJECT_ROOT, "pages")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# إضافة المسارات إلى sys.path
for path in [PROJECT_ROOT, BACKEND_DIR, OPPORTUNITY_DIR, PAGES_DIR, FRONTEND_DIR]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# ============================================================================
# رسائل الخطأ الودية
# ============================================================================

ERROR_MESSAGES = {
    'no_data': 'لا توجد بيانات كافية للسهم المحدد',
    'connection': 'مشكلة في الاتصال بمزود البيانات. تحقق من اتصال الإنترنت',
    'import': 'مشكلة في تحميل المحرك. تأكد من تثبيت جميع المكتبات',
    'unknown': 'حدث خطأ غير متوقع',
    'symbol_not_found': 'الرمز المحدد غير موجود. تأكد من صحة الرمز',
    'api_limit': 'تم تجاوز حد الاستخدام اليومي لواجهة API'
}

def show_user_friendly_error(error_type, details=None, exception=None):
    """عرض رسائل خطأ ودية للمستخدم"""
    message = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['unknown'])
    if details:
        message += f": {details}"
    
    st.error(f"❌ {message}")
    
    # في وضع التطوير، عرض التفاصيل الكاملة
    if exception and st.session_state.get('debug_mode', False):
        with st.expander("🔍 تفاصيل الخطأ (للمطورين)"):
            st.code(traceback.format_exc())
    
    # تسجيل الخطأ في السجل
    if exception:
        print(f"ERROR [{error_type}]: {str(exception)}")
        print(traceback.format_exc())

# ============================================================================
# استيراد المكونات - مع تجنب الـ Deadlock
# ============================================================================

try:
    from config import STOCK_SYMBOLS, APP_SETTINGS
except ImportError:
    STOCK_SYMBOLS = {
        'الكل': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD'],
        'التكنولوجيا': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD'],
        'المالية': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'V', 'MA'],
        'الصحية': ['JNJ', 'UNH', 'PFE', 'MRK', 'ABBV', 'TMO'],
        'الاستهلاكية': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'MCD'],
        'الطاقة': ['XOM', 'CVX', 'COP', 'SLB', 'EOG']
    }
    APP_SETTINGS = {'title': 'AI Breakout Scanner'}

# ============================================================================
# استيراد BreakoutScanner بشكل متأخر (لتجنب Deadlock)
# ============================================================================

_BreakoutScanner = None

def get_breakout_scanner():
    """استيراد BreakoutScanner فقط عند الحاجة"""
    global _BreakoutScanner
    if _BreakoutScanner is None:
        try:
            from backend.scanner.breakout_scanner import BreakoutScanner
            _BreakoutScanner = BreakoutScanner
            print("✅ تم استيراد BreakoutScanner")
        except ImportError as e:
            print(f"⚠️ فشل استيراد BreakoutScanner: {e}")
            try:
                import importlib.util
                scanner_path = os.path.join(BACKEND_DIR, "scanner", "breakout_scanner.py")
                if os.path.exists(scanner_path):
                    spec = importlib.util.spec_from_file_location("breakout_scanner", scanner_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    _BreakoutScanner = getattr(module, "BreakoutScanner", None)
                    if _BreakoutScanner:
                        print("✅ تم استيراد BreakoutScanner (importlib)")
            except Exception as e2:
                print(f"❌ فشل الاستيراد النهائي: {e2}")
                _BreakoutScanner = None
    return _BreakoutScanner

# ============================================================================
# استيراد محرك الفرص (Opportunity Engine)
# ============================================================================

OPPORTUNITY_AVAILABLE = False
OPPORTUNITY_PAGE_AVAILABLE = False
opportunity_page = None
OpportunityEngine = None
MarketPhase = None

def get_opportunity_engine_safe():
    """الحصول على محرك الفرص بشكل آمن"""
    try:
        from backend.opportunity.opportunity_engine import OpportunityEngine
        return OpportunityEngine()
    except ImportError:
        try:
            from opportunity.opportunity_engine import OpportunityEngine
            return OpportunityEngine()
        except ImportError:
            try:
                import importlib.util
                init_file = os.path.join(OPPORTUNITY_DIR, "__init__.py")
                if os.path.exists(init_file):
                    spec = importlib.util.spec_from_file_location("opportunity", init_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    OpportunityEngine = getattr(module, "OpportunityEngine", None)
                    if OpportunityEngine:
                        return OpportunityEngine()
            except Exception:
                pass
    return None

try:
    from opportunity import OpportunityEngine, MarketPhase
    OPPORTUNITY_AVAILABLE = True
    print("✅ تم استيراد محرك الفرص")
except ImportError:
    try:
        from backend.opportunity import OpportunityEngine, MarketPhase
        OPPORTUNITY_AVAILABLE = True
        print("✅ تم استيراد محرك الفرص (backend)")
    except ImportError:
        try:
            import importlib.util
            init_file = os.path.join(OPPORTUNITY_DIR, "__init__.py")
            if os.path.exists(init_file):
                spec = importlib.util.spec_from_file_location("opportunity", init_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                OpportunityEngine = getattr(module, "OpportunityEngine", None)
                MarketPhase = getattr(module, "MarketPhase", None)
                if OpportunityEngine:
                    OPPORTUNITY_AVAILABLE = True
                    print("✅ تم استيراد محرك الفرص (importlib)")
        except Exception:
            pass

if OPPORTUNITY_AVAILABLE:
    try:
        from opportunity_timeline import main as opportunity_page
        OPPORTUNITY_PAGE_AVAILABLE = True
        print("✅ تم استيراد صفحة الفرص")
    except ImportError:
        try:
            from pages.opportunity_timeline import main as opportunity_page
            OPPORTUNITY_PAGE_AVAILABLE = True
            print("✅ تم استيراد صفحة الفرص (pages)")
        except ImportError:
            try:
                page_file = os.path.join(PAGES_DIR, "opportunity_timeline.py")
                if os.path.exists(page_file):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("opportunity_timeline", page_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    opportunity_page = getattr(module, "main", None)
                    if opportunity_page:
                        OPPORTUNITY_PAGE_AVAILABLE = True
                        print("✅ تم استيراد صفحة الفرص (importlib)")
            except Exception:
                pass

print(f"🔍 محرك الفرص: {'✅ متوفر' if OPPORTUNITY_AVAILABLE else '❌ غير متوفر'}")
print(f"🔍 صفحة الفرص: {'✅ متوفرة' if OPPORTUNITY_PAGE_AVAILABLE else '❌ غير متوفرة'}")

# ============================================================================
# دوال مساعدة محسّنة
# ============================================================================

def get_symbols_by_sector(sector):
    if sector == 'الكل' or sector is None:
        if isinstance(STOCK_SYMBOLS, dict):
            all_symbols = []
            for syms in STOCK_SYMBOLS.values():
                if isinstance(syms, list):
                    all_symbols.extend(syms)
            # إزالة التكرارات
            return list(set(all_symbols))
        return STOCK_SYMBOLS
    if isinstance(STOCK_SYMBOLS, dict):
        return STOCK_SYMBOLS.get(sector, [])
    return STOCK_SYMBOLS

def get_sectors():
    if isinstance(STOCK_SYMBOLS, dict):
        return ['الكل'] + [s for s in STOCK_SYMBOLS.keys() if s != 'الكل']
    return ['الكل']

# ديكور لمعالجة الأخطاء
def safe_execute(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            show_user_friendly_error('unknown', str(e), e)
            return None
    return wrapper

# ============================================================================
# تحميل الاستايل مع دعم الثيم
# ============================================================================

def load_inline_css(theme='dark'):
    if theme == 'light':
        bg_gradient = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        card_bg = "rgba(255,255,255,0.08)"
        text_color = "#1a1a2e"
        text_secondary = "rgba(0,0,0,0.6)"
    else:
        bg_gradient = "linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)"
        card_bg = "rgba(255,255,255,0.04)"
        text_color = "#ffffff"
        text_secondary = "rgba(255,255,255,0.55)"
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_gradient};
    }}
    .main-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 8px 32px rgba(102,126,234,0.25);
    }}
    .main-header h1 {{
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    .main-header p {{
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }}
    [data-testid="stSidebar"] {{
        background: rgba(20,20,40,0.92) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    .stMarkdown, p, div, span, label {{
        color: {text_color} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}
    .metric-card {{
        background: {card_bg};
        border: 1px solid rgba(255,255,255,0.06);
        padding: 18px 20px;
        border-radius: 14px;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }}
    .metric-card .value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }}
    .metric-card .label {{
        font-size: 0.85rem;
        color: {text_secondary};
    }}
    .metric-card .icon {{
        font-size: 1.6rem;
        margin-bottom: 4px;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.25) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.35) !important;
    }}
    button[kind="primary"] {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        box-shadow: 0 4px 15px rgba(245,87,108,0.3) !important;
    }}
    button[kind="primary"]:hover {{
        box-shadow: 0 8px 25px rgba(245,87,108,0.4) !important;
    }}
    [data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }}
    [data-testid="stDataFrame"] thead th {{
        background: rgba(102,126,234,0.12) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }}
    [data-testid="stDataFrame"] tbody td {{
        color: #d0d0d0 !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: #1e1e38 !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
        border-radius: 10px !important;
        min-height: 42px !important;
    }}
    div[data-baseweb="select"] * {{
        color: #ffffff !important;
        font-weight: 600 !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: #667eea !important;
    }}
    div[data-baseweb="popover"] div[role="listbox"],
    ul[data-baseweb="menu"] {{
        background-color: #16162a !important;
        border: 1px solid rgba(102, 126, 234, 0.5) !important;
        border-radius: 12px !important;
    }}
    div[data-baseweb="popover"] li,
    ul[data-baseweb="menu"] li {{
        background-color: transparent !important;
        color: #e0e0e0 !important;
        padding: 10px 16px !important;
    }}
    div[data-baseweb="popover"] li:hover,
    ul[data-baseweb="menu"] li:hover {{
        background: rgba(102, 126, 234, 0.25) !important;
        color: #ffffff !important;
    }}
    div[data-baseweb="popover"] li[aria-selected="true"],
    ul[data-baseweb="menu"] li[aria-selected="true"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
    }}
    .stTextInput > div > div > input {{
        background-color: #1e1e38 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: rgba(255, 255, 255, 0.4) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }}
    .stAlert {{
        background: rgba(255,255,255,0.04) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }}
    .engine-status {{
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        font-size: 0.85rem;
    }}
    .engine-status-active {{
        background: rgba(0, 230, 118, 0.15);
        border: 1px solid rgba(0, 230, 118, 0.3);
        color: #00E676;
    }}
    .engine-status-inactive {{
        background: rgba(255, 82, 82, 0.15);
        border: 1px solid rgba(255, 82, 82, 0.3);
        color: #FF5252;
    }}
    .badge-new {{
        background: #f5576c;
        color: white;
        font-size: 0.6rem;
        padding: 1px 8px;
        border-radius: 10px;
        margin-left: 5px;
        font-weight: 700;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    .alert-box {{
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
    }}
    .alert-box.info {{
        background: rgba(41, 182, 246, 0.1);
        border-color: rgba(41, 182, 246, 0.3);
    }}
    .alert-box.success {{
        background: rgba(0, 230, 118, 0.1);
        border-color: rgba(0, 230, 118, 0.3);
    }}
    .alert-box.warning {{
        background: rgba(255, 193, 7, 0.1);
        border-color: rgba(255, 193, 7, 0.3);
    }}
    .alert-box.danger {{
        background: rgba(255, 82, 82, 0.1);
        border-color: rgba(255, 82, 82, 0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

def load_css():
    """تحميل الـ CSS مع دعم الثيم"""
    theme = st.session_state.get('theme', 'dark')
    css_path = os.path.join(PROJECT_ROOT, "assets", "style.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        except Exception:
            load_inline_css(theme)
    else:
        load_inline_css(theme)

# ============================================================================
# تهيئة حالة الجلسة المحسّنة
# ============================================================================

def init_session_state():
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
        'custom_symbol_input': '',
        'opportunity_results': {},
        'debug_info': {
            'opportunity_available': OPPORTUNITY_AVAILABLE,
            'opportunity_page_available': OPPORTUNITY_PAGE_AVAILABLE,
        },
        'theme': 'dark',
        'debug_mode': False,
        'results_history': [],  # تاريخ النتائج
        'favorites': [],  # الأسهم المفضلة
        'alerts': [],  # التنبيهات
        'last_alert_check': None
    }
    if not st.session_state.get('initialized', False):
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state.initialized = True

# ============================================================================
# دوال إدارة النتائج والتنبيهات
# ============================================================================

def save_scan_result(results):
    """حفظ نتائج المسح في التاريخ"""
    if results is not None and not results.empty:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.session_state.results_history.append({
            'timestamp': timestamp,
            'results': results.copy(),
            'config': st.session_state.sidebar_config.copy()
        })
        # الاحتفاظ بآخر 20 نتيجة فقط
        if len(st.session_state.results_history) > 20:
            st.session_state.results_history.pop(0)

def check_alerts(results):
    """فحص التنبيهات بناءً على النتائج"""
    alerts = []
    if results is not None and not results.empty:
        for _, row in results.iterrows():
            symbol = row.get('symbol', '')
            score = row.get('score', 0)
            squeeze = row.get('squeeze', 0)
            
            if score >= 80:
                alerts.append(f"🔔 **{symbol}**: فرصة قوية جداً ({score}%)")
            elif score >= 70:
                alerts.append(f"📈 **{symbol}**: فرصة جيدة ({score}%)")
            
            if squeeze >= 85:
                alerts.append(f"📊 **{symbol}**: ضغط عالي - استعداد للانفجار")
            
            # تنبيهات المخاطرة
            risk = row.get('risk', '')
            if risk == 'مرتفع' and score >= 70:
                alerts.append(f"⚠️ **{symbol}**: فرصة عالية المخاطرة")
    
    return alerts

def export_results(results, format='csv'):
    """تصدير النتائج بتنسيقات متعددة"""
    if results is None or results.empty:
        return None
    
    if format == 'csv':
        return results.to_csv(index=False)
    elif format == 'json':
        return results.to_json(orient='records', date_format='iso')
    elif format == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            results.to_excel(writer, index=False, sheet_name='Scan Results')
        return output.getvalue()
    return None

def toggle_theme():
    """تبديل الثيم"""
    current = st.session_state.theme
    st.session_state.theme = 'light' if current == 'dark' else 'dark'
    st.rerun()

# ============================================================================
# الشريط الجانبي المحسّن
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
        
        # تبديل الثيم
        theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
        if st.button(f"{theme_icon} تبديل الثيم", use_container_width=True):
            toggle_theme()
        
        st.markdown("---")
        
        # قائمة الصفحات
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🚀 AI Opportunity Timeline": "opportunity",
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
            key="nav_radio",
            format_func=lambda x: x + " 🆕" if x == "🚀 AI Opportunity Timeline" else x
        )
        
        new_page = pages[selected]
        if new_page != current_page:
            st.session_state.current_page = new_page
            st.rerun()
        
        st.markdown("---")
        
        # إعدادات المسح (للصفحات غير opportunity)
        if new_page != "opportunity":
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
        
        # عرض المفضلة
        if st.session_state.get('favorites'):
            st.subheader("⭐ المفضلة")
            for fav in st.session_state.favorites[:5]:
                st.caption(f"• {fav}")
        
        # معلومات إضافية
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # حالة النظام
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
        
        # وضع التطوير
        debug_mode = st.checkbox(
            "🐛 وضع التطوير",
            value=st.session_state.get('debug_mode', False),
            key="debug_mode_checkbox"
        )
        st.session_state.debug_mode = debug_mode
        
        return st.session_state.sidebar_config

# ============================================================================
# تحليل السهم المحسّن
# ============================================================================

@safe_execute
def display_stock_analysis(symbol):
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        try:
            import yfinance as yf
            import plotly.graph_objects as go
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            
            if df.empty:
                show_user_friendly_error('symbol_not_found', symbol)
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
            
            # عرض المؤشرات الرئيسية
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
            
            # الرسم البياني
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
                
                # نسبة الحجم
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
            
            # الأخبار
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
            show_user_friendly_error('unknown', str(e), e)

def render_analyze():
    st.subheader("📈 تحليل سهم محدد")
    
    MAIN_SYMBOLS = {
        'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corp.', 'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.', 'NVDA': 'NVIDIA Corp.', 'META': 'Meta Platforms',
        'TSLA': 'Tesla Inc.', 'AMD': 'Advanced Micro Devices', 'INTC': 'Intel Corp.',
        'NFLX': 'Netflix Inc.', 'PYPL': 'PayPal Holdings', 'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce Inc.', 'ORCL': 'Oracle Corp.', 'IBM': 'IBM Corp.',
        'CSCO': 'Cisco Systems', 'QCOM': 'Qualcomm Inc.', 'TXN': 'Texas Instruments',
        'JPM': 'JPMorgan Chase', 'BAC': 'Bank of America', 'WFC': 'Wells Fargo',
        'JNJ': 'Johnson & Johnson', 'UNH': 'UnitedHealth', 'PFE': 'Pfizer Inc.',
        'WMT': 'Walmart Inc.', 'PG': 'Procter & Gamble', 'KO': 'Coca-Cola Co.',
        'XOM': 'Exxon Mobil', 'CVX': 'Chevron Corp.', 'V': 'Visa Inc.', 'MA': 'Mastercard Inc.'
    }
    
    if 'custom_symbols' in st.session_state:
        MAIN_SYMBOLS.update(st.session_state.custom_symbols)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.02); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <p style="margin:0; color: rgba(255,255,255,0.6); font-size: 0.85rem;">
            💡 اختر من الرموز الرئيسية أو اكتب رمزاً مخصصاً
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        symbol_options = ["-- اختر رمزاً --"] + list(MAIN_SYMBOLS.keys()) + ["✏️ إدخال مخصص"]
        selected_option = st.selectbox("اختر رمز السهم:", options=symbol_options, index=0, key="symbol_select_main")
        
        if selected_option == "✏️ إدخال مخصص":
            symbol = st.text_input(
                "أدخل رمز السهم:",
                value=st.session_state.get('custom_symbol_input', ''),
                placeholder="مثال: AAPL, MSFT, TSLA...",
                key="custom_symbol_input_main"
            ).upper().strip()
            
            if symbol and symbol not in MAIN_SYMBOLS:
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
        refresh_clicked = st.button("🔄 تحديث", type="primary", use_container_width=True, key="refresh_analysis_main")
    
    if symbol:
        if refresh_clicked:
            st.cache_data.clear()
        display_stock_analysis(symbol)
    else:
        st.info("🔍 اختر أو اكتب رمز سهم للبدء")

# ============================================================================
# الصفحات المحسّنة
# ============================================================================

def render_dashboard():
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
        # عدد التنبيهات النشطة
        alerts = st.session_state.get('alerts', [])
        alert_count = len(alerts)
        alert_color = "#FF5252" if alert_count > 0 else "#29B6F6"
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🔔</div>
            <div class="value" style="color:{alert_color};">{alert_count}</div>
            <div class="label">تنبيهات نشطة</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # عرض التنبيهات
    alerts = st.session_state.get('alerts', [])
    if alerts:
        st.subheader("🔔 التنبيهات")
        for alert in alerts[:5]:
            if '🔔' in alert or '📈' in alert:
                st.success(alert)
            elif '⚠️' in alert:
                st.warning(alert)
            else:
                st.info(alert)
        if len(alerts) > 5:
            st.caption(f"... و {len(alerts) - 5} تنبيهات إضافية")
    
    st.markdown("---")
    
    # حالة المحرك
    st.subheader("🧠 حالة محرك الذكاء الاصطناعي")
    col1, col2 = st.columns(2)
    
    with col1:
        if OPPORTUNITY_AVAILABLE:
            st.success("✅ محرك الفرص: نشط وجاهز للعمل")
            st.caption("يمكنك استخدام صفحة 'AI Opportunity Timeline' للتحليل المتقدم")
        else:
            st.error("❌ محرك الفرص: غير متوفر")
    
    with col2:
        if OPPORTUNITY_PAGE_AVAILABLE:
            st.success("✅ صفحة الفرص: متوفرة")
        else:
            st.error("❌ صفحة الفرص: غير متوفرة")
    
    st.markdown("---")
    
    # عرض آخر النتائج
    results = st.session_state.get('scan_results', pd.DataFrame())
    if not results.empty:
        st.subheader("📋 أفضل الفرص")
        st.dataframe(
            results.head(10),
            column_config={
                "symbol": "الرمز",
                "score": st.column_config.ProgressColumn("الدرجة", format="%.0f/100", min_value=0, max_value=100),
                "squeeze": st.column_config.ProgressColumn("الانضغاط", format="%.0f/100", min_value=0, max_value=100),
                "recommendation": "التوصية",
                "risk": "المخاطرة",
                "price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "target": st.column_config.NumberColumn("الهدف", format="$%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("🔍 اضغط 'بدء المسح' في الشريط الجانبي للبدء")
    
    # عرض تاريخ النتائج
    if st.session_state.get('results_history'):
        with st.expander("📜 تاريخ التحليلات السابقة"):
            history = st.session_state.results_history[-5:]  # آخر 5 تحليلات
            for item in reversed(history):
                st.caption(f"🕐 {item['timestamp']}")
                st.dataframe(
                    item['results'].head(3),
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown("---")

# دالة مسح السوق المحسّنة
@st.cache_data(ttl=300)  # تخزين مؤقت لمدة 5 دقائق
def cached_scan_market(_symbols, min_score):
    """مسح السوق مع تخزين مؤقت"""
    scanner = get_breakout_scanner()
    if scanner:
        try:
            return scanner().scan_market(_symbols, min_score=min_score)
        except Exception as e:
            print(f"خطأ في المسح: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def render_scanner():
    st.subheader("🔍 مسح السوق")
    
    config = st.session_state.get('sidebar_config', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 الحد الأدنى للدرجة", f"{config.get('min_score', 60)}/100")
    with col2:
        st.metric("📊 عدد الأسهم", f"{config.get('max_symbols', 15)}")
    with col3:
        st.metric("🤖 النموذج", "Random Forest")
    
    st.markdown("---")
    
    sectors = get_sectors()
    selected_sector = st.selectbox("🏢 تصفية حسب القطاع", sectors, index=0, key="scanner_sector")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        scan_clicked = st.button("🔄 تحديث النتائج", type="primary", use_container_width=True)
    with col2:
        export_format = st.selectbox("📥 تنسيق التصدير", ['csv', 'json', 'excel'], key="export_format")
    
    if scan_clicked:
        with st.spinner("🔍 جاري مسح السوق..."):
            try:
                symbols = get_symbols_by_sector(selected_sector)
                symbols = symbols[:config.get('max_symbols', 15)]
                
                # استخدام المسح المخزن مؤقتاً
                results = cached_scan_market(tuple(symbols), config.get('min_score', 60))
                
                if results is not None and not results.empty:
                    st.session_state.scan_results = results
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    
                    # حفظ النتائج
                    save_scan_result(results)
                    
                    # فحص التنبيهات
                    alerts = check_alerts(results)
                    if alerts:
                        st.session_state.alerts = alerts
                        st.session_state.last_alert_check = datetime.now()
                        
                        # عرض التنبيهات
                        st.warning("⚠️ **تنبيهات مكتشفة:**")
                        for alert in alerts[:3]:
                            st.info(f"• {alert}")
                        if len(alerts) > 3:
                            st.caption(f"... و {len(alerts) - 3} تنبيهات إضافية")
                    
                    st.success(f"✅ تم العثور على {len(results)} فرصة!")
                else:
                    st.warning("⚠️ لا توجد نتائج مطابقة للمعايير")
                    st.session_state.scan_results = pd.DataFrame()
                    
            except Exception as e:
                show_user_friendly_error('unknown', str(e), e)
    
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    if not results.empty:
        st.subheader(f"📊 النتائج ({len(results)})")
        st.dataframe(results, use_container_width=True, hide_index=True)
        
        # زر التصدير
        export_data = export_results(results, export_format)
        if export_data:
            file_ext = 'csv' if export_format == 'csv' else 'json' if export_format == 'json' else 'xlsx'
            mime_type = 'text/csv' if export_format == 'csv' else 'application/json' if export_format == 'json' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            st.download_button(
                f"📥 تحميل {export_format.upper()}",
                export_data,
                f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.{file_ext}",
                mime_type,
                use_container_width=True
            )
        
        # عرض إحصائيات سريعة
        st.markdown("---")
        st.subheader("📊 إحصائيات سريعة")
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = results['score'].mean() if 'score' in results.columns else 0
            st.metric("متوسط الدرجة", f"{avg_score:.1f}/100")
        with col2:
            high_score = len(results[results['score'] >= 80]) if 'score' in results.columns else 0
            st.metric("فرص قوية (≥80%)", high_score)
        with col3:
            low_risk = len(results[results.get('risk', '') == 'منخفض']) if 'risk' in results.columns else 0
            st.metric("فرص منخفضة المخاطرة", low_risk)

def render_market_data():
    try:
        from frontend.pages.market_data import render as render_market_data_page
        render_market_data_page()
    except ImportError:
        st.warning("⚠️ صفحة بيانات السوق غير متوفرة حالياً")
        st.info("💡 تأكد من وجود ملف frontend/pages/market_data.py")

def render_opportunity_page():
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
            <div style="background: rgba(255,255,255,0.2); padding: 4px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                🆕 NEW
            </div>
        </div>
        <p style="margin-top: 5px; opacity: 0.9; font-size: 0.95rem;">
            تحليل الفرص الاستثمارية المتقدم باستخدام الذكاء الاصطناعي
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not OPPORTUNITY_AVAILABLE:
        st.error("❌ **محرك الفرص غير متوفر**")
        st.warning("""
        **الأسباب المحتملة:**
        1. **الملفات غير موجودة** - تأكد من وجود مجلد `backend/opportunity/` مع جميع الملفات
        2. **أخطاء في الاستيراد** - قد تكون هناك أخطاء في ملفات المحرك
        3. **مسار غير صحيح** - تأكد من أن المسار مضاف بشكل صحيح
        """)
        
        if st.button("🔄 محاولة إعادة تحميل المحرك", type="primary"):
            st.rerun()
        return
    
    if not OPPORTUNITY_PAGE_AVAILABLE:
        st.error("❌ **صفحة الفرص غير متوفرة**")
        st.info("""
        **لتفعيل صفحة الفرص:**
        1. تأكد من وجود ملف `frontend/pages/opportunity_timeline.py`
        2. تأكد من أن الملف يحتوي على دالة `main()`
        3. أعد تشغيل التطبيق
        """)
        return
    
    try:
        opportunity_page()
    except Exception as e:
        show_user_friendly_error('unknown', str(e), e)

# ============================================================================
# عرض الصفحة المختارة
# ============================================================================

def render_current_page():
    page = st.session_state.get('current_page', 'dashboard')
    pages = {
        'dashboard': render_dashboard,
        'scanner': render_scanner,
        'analyze': render_analyze,
        'market_data': render_market_data,
        'opportunity': render_opportunity_page,
    }
    pages.get(page, render_dashboard)()

# ============================================================================
# التشغيل الرئيسي
# ============================================================================

def main():
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
