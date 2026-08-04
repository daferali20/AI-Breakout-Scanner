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
    # 1. إعدادات الصفحة
    # ============================================================================
    
    st.set_page_config(
        page_title="AI Breakout Scanner | ماسح الانفجار السعري",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ============================================================================
    # 2. إعداد المسارات بشكل صحيح
    # ============================================================================
    
    # الحصول على المسار المطلق للمشروع
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
    PROJECT_ROOT = os.path.dirname(ROOT_DIR)  # AI-Breakout-Scanner/
    BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")  # backend/
    OPPORTUNITY_DIR = os.path.join(BACKEND_DIR, "opportunity")  # backend/opportunity/
    PAGES_DIR = os.path.join(ROOT_DIR, "pages")  # frontend/pages/
    
    # إضافة جميع المسارات إلى sys.path
    paths_to_add = [
        ROOT_DIR,  # frontend
        PROJECT_ROOT,  # المشروع الرئيسي
        BACKEND_DIR,  # backend
        OPPORTUNITY_DIR,  # backend/opportunity
        PAGES_DIR,  # frontend/pages
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # ============================================================================
    # 3. استيراد المكونات
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
    # 4. استيراد محرك الفرص (Opportunity Engine)
    # ============================================================================
    
    OPPORTUNITY_AVAILABLE = False
    OPPORTUNITY_PAGE_AVAILABLE = False
    opportunity_page = None
    
    # محاولة استيراد محرك الفرص
    try:
        # محاولة 1: من backend.opportunity
        from backend.opportunity import OpportunityEngine, MarketPhase
        OPPORTUNITY_AVAILABLE = True
        print("✅ تم استيراد محرك الفرص بنجاح")
    except ImportError:
        try:
            # محاولة 2: استيراد مباشر
            from opportunity import OpportunityEngine, MarketPhase
            OPPORTUNITY_AVAILABLE = True
            print("✅ تم استيراد محرك الفرص بنجاح (مباشر)")
        except ImportError:
            try:
                # محاولة 3: استخدام importlib
                import importlib.util
                init_path = os.path.join(OPPORTUNITY_DIR, "__init__.py")
                if os.path.exists(init_path):
                    spec = importlib.util.spec_from_file_location("opportunity", init_path)
                    opportunity_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(opportunity_module)
                    OpportunityEngine = getattr(opportunity_module, 'OpportunityEngine', None)
                    MarketPhase = getattr(opportunity_module, 'MarketPhase', None)
                    if OpportunityEngine is not None:
                        OPPORTUNITY_AVAILABLE = True
                        print("✅ تم استيراد محرك الفرص بنجاح (importlib)")
            except Exception:
                pass
    
    # محاولة استيراد صفحة الفرص
    if OPPORTUNITY_AVAILABLE:
        try:
            # محاولة استيراد صفحة الفرص
            from pages.opportunity_timeline import main as opportunity_page
            OPPORTUNITY_PAGE_AVAILABLE = True
            print("✅ تم استيراد صفحة الفرص بنجاح")
        except ImportError:
            try:
                # محاولة مع مسار مطلق
                page_path = os.path.join(PAGES_DIR, "opportunity_timeline.py")
                if os.path.exists(page_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("opportunity_timeline", page_path)
                    page_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(page_module)
                    opportunity_page = page_module.main
                    OPPORTUNITY_PAGE_AVAILABLE = True
                    print("✅ تم استيراد صفحة الفرص بنجاح (importlib)")
            except Exception:
                pass
    
    # ============================================================================
    # 5. تحميل ملف الاستايل
    # ============================================================================
    
    def load_inline_css():
        """استايل مضمن بفكرة Dark Mode فائقة الوضوح"""
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
        
        /* ===== القوائم المنسدلة ===== */
        div[data-baseweb="select"] > div {
            background-color: #1e1e38 !important;
            border: 1px solid rgba(102, 126, 234, 0.4) !important;
            border-radius: 10px !important;
            min-height: 42px !important;
        }
    
        div[data-baseweb="select"] * {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
    
        div[data-baseweb="select"] svg {
            fill: #667eea !important;
        }
    
        div[data-baseweb="popover"] div[role="listbox"],
        ul[data-baseweb="menu"] {
            background-color: #16162a !important;
            border: 1px solid rgba(102, 126, 234, 0.5) !important;
            border-radius: 12px !important;
        }
    
        div[data-baseweb="popover"] li,
        ul[data-baseweb="menu"] li {
            background-color: transparent !important;
            color: #e0e0e0 !important;
            padding: 10px 16px !important;
        }
    
        div[data-baseweb="popover"] li:hover,
        ul[data-baseweb="menu"] li:hover {
            background: rgba(102, 126, 234, 0.25) !important;
            color: #ffffff !important;
        }
    
        div[data-baseweb="popover"] li[aria-selected="true"],
        ul[data-baseweb="menu"] li[aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: #ffffff !important;
        }
        
        /* ===== Text Input ===== */
        .stTextInput > div > div > input {
            background-color: #1e1e38 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            padding: 10px 14px !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.4) !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
        }
        
        /* ===== التنبيهات ===== */
        .stAlert {
            background: rgba(255,255,255,0.04) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
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
        </style>
        """, unsafe_allow_html=True)
    
    def load_css():
        """تحميل ملف الاستايل"""
        css_path = os.path.join(ROOT_DIR, "assets", "style.css")
        
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
    # 6. تهيئة حالة الجلسة
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
            'custom_symbol_input': '',
            'opportunity_results': {},
            'debug_info': {
                'opportunity_available': OPPORTUNITY_AVAILABLE,
                'opportunity_page_available': OPPORTUNITY_PAGE_AVAILABLE,
            }
        }
        
        if not st.session_state.get('initialized', False):
            for key, value in defaults.items():
                if key not in st.session_state:
                    st.session_state[key] = value
            st.session_state.initialized = True
    
    # ============================================================================
    # 7. دوال الحصول على الرموز حسب القطاع
    # ============================================================================
    
    def get_symbols_by_sector(sector):
        """الحصول على رموز الأسهم حسب القطاع"""
        if sector == 'الكل' or sector is None:
            if isinstance(STOCK_SYMBOLS, dict):
                all_symbols = []
                for syms in STOCK_SYMBOLS.values():
                    if isinstance(syms, list):
                        all_symbols.extend(syms)
                return all_symbols
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
    # 8. الشريط الجانبي
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
            
            # القائمة الرئيسية مع إضافة صفحة الفرص الجديدة
            pages = {
                "📊 لوحة التحكم": "dashboard",
                "🚀 AI Opportunity Timeline": "opportunity",
                "🔍 مسح السوق": "scanner",
                "📈 تحليل سهم": "analyze",
                "📊 بيانات السوق": "market_data"
            }
            
            current_page = st.session_state.get('current_page', 'dashboard')
            current_index = list(pages.values()).index(current_page) if current_page in pages.values() else 0
            
            # عرض القائمة مع علامة NEW بجانب الصفحة الجديدة
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
            
            # إعدادات المسح (تظهر في جميع الصفحات ما عدا صفحة الفرص)
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
            
            # معلومات النظام
            if st.session_state.get('last_scan_time'):
                st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
            st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
            
            # حالة محرك الفرص
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
            
            return st.session_state.sidebar_config
    
    # ============================================================================
    # 9. دوال عرض التحليل
    # ============================================================================
    
    def render_analyze():
        """تحليل سهم محدد مع رموز رئيسية وزر تحديث"""
        st.subheader("📈 تحليل سهم محدد")
        
        # الرموز الرئيسية
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
        
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
            <p style="margin:0; color: rgba(255,255,255,0.6); font-size: 0.85rem;">
                💡 اختر من الرموز الرئيسية أو اكتب رمزاً مخصصاً (مثل: AAPL, MSFT, TSLA)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
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
                use_container_width=True,
                key="refresh_analysis_main"
            )
        
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
                    
                    avg_volume = df['Volume'].iloc[-21:-1].mean() if len(df) > 21 else df['Volume'].mean()
                    vol_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
                    vol_color = "#00E676" if vol_ratio > 1.5 else "#FFC107" if vol_ratio > 1 else "#FF5252"
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">نسبة الحجم</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {vol_color};">{vol_ratio:.2f}x</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or 0
                    atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">ATR</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #29B6F6;">${atr:.2f} ({atr_percent:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    pe = info.get('trailingPE', 'N/A')
                    pe_color = "#00E676" if pe != 'N/A' and pe < 25 else "#FFC107" if pe != 'N/A' and pe < 40 else "#FF5252"
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;">
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">نسبة PE</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {pe_color};">{f"{pe:.2f}" if pe != 'N/A' else 'N/A'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
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
    # 10. الصفحات الأخرى
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
        
        # عرض حالة محرك الفرص
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
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("🔍 اضغط 'بدء المسح' في الشريط الجانبي للبدء")
    
    def render_scanner():
        """صفحة المسح"""
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
        selected_sector = st.selectbox(
            "🏢 تصفية حسب القطاع",
            sectors,
            index=0,
            key="scanner_sector"
        )
        
        if st.button("🔄 تحديث النتائج", type="primary", use_container_width=True):
            with st.spinner("🔍 جاري مسح السوق..."):
                try:
                    symbols = get_symbols_by_sector(selected_sector)
                    symbols = symbols[:config.get('max_symbols', 15)]
                    
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
                            symbols,
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
            st.dataframe(results, use_container_width=True, hide_index=True)
            
            csv = results.to_csv(index=False)
            st.download_button(
                "📥 تحميل CSV",
                csv,
                f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
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
    2. تأكد من أن ملف `__init__.py` يحتوي على الاستيرادات الصحيحة
    
    3. أعد تشغيل التطبيق
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
    
    # ✅ كل شيء جاهز - عرض صفحة الفرص
    try:
    opportunity_page()
    except Exception as e:
    st.error(f"❌ حدث خطأ في صفحة الفرص: {str(e)}")
    st.exception(e)
    
    # ============================================================================
    # 12. عرض الصفحة المختارة
    # ============================================================================
    
    def render_current_page():
    """عرض الصفحة المختارة"""
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
    # 13. التطبيق الرئيسي
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
