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
    page_title="AI Breakout Scanner",
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

from config import STOCK_SYMBOLS, APP_SETTINGS
from backend.scanner.breakout_scanner import BreakoutScanner

# ============================================================================
# تهيئة حالة الجلسة
# ============================================================================

def init_session_state():
    defaults = {
        'scan_results': pd.DataFrame(),
        'current_page': 'dashboard',
        'scan_in_progress': False,
        'last_scan': None,
        'selected_symbol': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# التصميم
# ============================================================================

def load_css():
    """تحميل التصميم ثلاثي الأبعاد"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px -10px rgba(0,0,0,0.4);
    }
    .main-header h1 {
        font-size: 2rem;
        margin: 0;
        font-weight: 800;
    }
    .main-header p {
        opacity: 0.9;
        margin-top: 5px;
        font-size: 1rem;
    }
    [data-testid="stSidebar"] {
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.4);
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
    }
    .metric-card .label {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# المكونات
# ============================================================================

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:10px 0;">
            <h2 style="color:#667eea; margin:0;">🚀 AI Scanner</h2>
            <p style="color:rgba(255,255,255,0.6); font-size:0.9rem;">اكتشاف الانفجارات السعرية</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # القائمة
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🔍 مسح السوق": "scanner",
            "📈 تحليل سهم": "analyze"
        }
        
        selected = st.radio(
            "القائمة",
            list(pages.keys()),
            index=0,
            key="nav_radio"
        )
        st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # إعدادات المسح
        st.subheader("⚙️ إعدادات المسح")
        
        min_score = st.slider(
            "الحد الأدنى للدرجة",
            min_value=40,
            max_value=90,
            value=60,
            step=5,
            key="min_score"
        )
        
        max_symbols = st.slider(
            "عدد الأسهم للمسح",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            key="max_symbols"
        )
        
        if st.button("🚀 بدء المسح", type="primary", width="stretch"):
            st.session_state.scan_in_progress = True
            st.session_state.current_page = "scanner"
        
        st.markdown("---")
        
        if st.session_state.get('last_scan'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan}")
        
        return {'min_score': min_score, 'max_symbols': max_symbols}

def render_dashboard():
    """لوحة التحكم"""
    st.subheader("📊 نظرة عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="value">150+</div>
            <div class="label">أسهم متاحة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        results = st.session_state.scan_results
        count = len(results) if not results.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="value" style="color:#00E676;">{count}</div>
            <div class="label">فرص مكتشفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="value" style="color:#FFD700;">84%</div>
            <div class="label">دقة النموذج</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="value" style="color:#29B6F6;">AI</div>
            <div class="label">ذكاء اصطناعي</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # عرض النتائج
    if not st.session_state.scan_results.empty:
        st.subheader("📋 أفضل الفرص")
        st.dataframe(
            st.session_state.scan_results,
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
    
    # عرض الإعدادات
    config = st.session_state.get('sidebar_config', {'min_score': 60, 'max_symbols': 15})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 الحد الأدنى للدرجة", f"{config.get('min_score', 60)}/100")
    with col2:
        st.metric("📊 عدد الأسهم", f"{config.get('max_symbols', 15)}")
    with col3:
        st.metric("🤖 النموذج", "Random Forest")
    
    st.markdown("---")
    
    # زر المسح
    if st.button("🔄 تحديث النتائج", type="primary", width="stretch"):
        with st.spinner("🔍 جاري مسح السوق..."):
            scanner = BreakoutScanner()
            results = scanner.scan_market(
                STOCK_SYMBOLS[:config.get('max_symbols', 15)],
                min_score=config.get('min_score', 60)
            )
            
            if not results.empty:
                st.session_state.scan_results = results
                st.session_state.last_scan = datetime.now().strftime('%H:%M:%S')
                st.success(f"✅ تم العثور على {len(results)} فرصة!")
            else:
                st.warning("⚠️ لا توجد نتائج مطابقة للمعايير")
    
    # عرض النتائج
    if not st.session_state.scan_results.empty:
        st.subheader(f"📊 النتائج ({len(st.session_state.scan_results)})")
        st.dataframe(
            st.session_state.scan_results,
            width='stretch',
            hide_index=True
        )
        
        # تصدير
        csv = st.session_state.scan_results.to_csv(index=False)
        st.download_button(
            "📥 تحميل CSV",
            csv,
            f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            width="stretch"
        )

def render_analyze():
    """تحليل سهم"""
    st.subheader("📈 تحليل سهم محدد")
    
    symbol = st.text_input(
        "أدخل رمز السهم",
        value="AAPL",
        key="symbol_input"
    ).upper()
    
    if symbol:
        with st.spinner(f"📊 جاري تحليل {symbol}..."):
            scanner = BreakoutScanner()
            result = scanner.scan_stock(symbol)
            
            if 'error' in result:
                st.error(f"❌ {result['error']}")
                return
            
            # عرض النتائج
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### 🎯 {symbol}")
                
                # المؤشرات
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("الدرجة", f"{result['score']}/100")
                with col_b:
                    st.metric("التوصية", result['recommendation']['action'])
                with col_c:
                    st.metric("المخاطرة", result['recommendation']['risk'])
                
                st.markdown("---")
                
                # مستويات التداول
                st.markdown("#### 📍 مستويات التداول")
                levels = result['levels']
                st.write(f"💰 السعر الحالي: **${levels['current']:.2f}**")
                st.write(f"📈 نقطة الدخول: **${levels['entry']:.2f}**")
                st.write(f"🛑 وقف الخسارة: **${levels['stop_loss']:.2f}**")
                st.write(f"🎯 الهدف 1: **${levels['target_1']:.2f}**")
                st.write(f"🎯 الهدف 2: **${levels['target_2']:.2f}**")
            
            with col2:
                # مؤشرات إضافية
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

# ============================================================================
# التطبيق الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية"""
    
    # تحميل التصميم
    load_css()
    
    # عرض الهيدر
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Breakout Scanner</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي ومؤشرات الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض الشريط الجانبي
    config = render_sidebar()
    st.session_state.sidebar_config = config
    
    # عرض الصفحة المختارة
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'scanner':
        render_scanner()
    elif page == 'analyze':
        render_analyze()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
