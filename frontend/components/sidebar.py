# frontend/components/sidebar.py - إضافة صفحة بيانات السوق
"""
مكون الشريط الجانبي - مع إضافة صفحة بيانات السوق
"""

import streamlit as st
from datetime import datetime

def set_page(page_name):
    st.session_state.current_page = page_name

def render_sidebar():
    with st.sidebar:
        st.title("🤖 AI Breakout Scanner")
        st.markdown("---")
        
        # أزرار التنقل الرئيسية مع ربطها بحالة الجلسة مباشره
        st.button(
            "📊 اللوحة الرئيسية (Dashboard)", 
            on_click=set_page, 
            args=("Dashboard",),
            use_container_width=True
        )
        st.button(
            "🔍 تحليل سهم (Analyze)", 
            on_click=set_page, 
            args=("Analyze",),
            use_container_width=True
        )
        st.button(
            "📈 بيانات السوق (Market Data)", 
            on_click=set_page, 
            args=("Market Data",),
            use_container_width=True
        )
        
        st.markdown("---")
        st.caption("إصدار النظام: v2.0.0")
def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 AI Scanner")
        st.markdown("---")
        
        # القائمة الرئيسية - مع إضافة صفحة بيانات السوق
        render_main_menu()
        
        st.markdown("---")
        
        # إعدادات المسح
        render_scan_settings()
        
        st.markdown("---")
        
        # معلومات النظام
        render_system_info()
        
        return st.session_state.get('sidebar_config', {})

def render_main_menu():
    """عرض القائمة الرئيسية - مع إضافة بيانات السوق"""
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 مسح السوق": "scanner",
        "📈 تحليل سهم": "analyze",
        "📊 بيانات السوق": "market_data"  # الصفحة الجديدة
    }
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # العثور على الفهرس الحالي
    current_index = 0
    for i, (key, value) in enumerate(pages.items()):
        if value == current_page:
            current_index = i
            break
    
    selected = st.radio(
        "القائمة", 
        list(pages.keys()), 
        index=current_index,
        key="main_menu_radio"
    )
    
    new_page = pages[selected]
    if new_page != current_page:
        st.session_state.current_page = new_page

def render_scan_settings():
    """عرض إعدادات المسح"""
    st.subheader("⚙️ إعدادات المسح")
    
    if 'sidebar_config' not in st.session_state:
        st.session_state.sidebar_config = {}
    
    config = st.session_state.sidebar_config
    
    min_score = st.slider(
        "🎯 درجة الجاهزية", 
        40, 90, 
        config.get('min_score', 60) if config else 60,
        step=5,
        key="min_score_slider"
    )
    
    max_symbols = st.slider(
        "📈 عدد الأسهم للمسح",
        5, 30, 
        config.get('max_symbols', 15) if config else 15,
        step=5,
        key="max_symbols"
    )
    
    scan_clicked = st.button(
        "🔍 ابدأ المسح", 
        width="stretch",
        type="primary",
        key="scan_button"
    )
    
    st.session_state.sidebar_config = {
        'min_score': min_score,
        'max_symbols': max_symbols,
        'scan_clicked': scan_clicked
    }

def render_system_info():
    """عرض معلومات النظام"""
    if st.session_state.get('last_scan_time'):
        st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("💡 بيانات السوق محدثة لحظياً")
