"""
مكون الشريط الجانبي (Sidebar) - AI Breakout Scanner
يتضمن التنقل بين الصفحات وإعدادات المسح
"""

import streamlit as st
from datetime import datetime

def render_sidebar():
    """عرض الشريط الجانبي بالكامل وإرجاع الإعدادات المختارة"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 AI Scanner")
        st.markdown("---")
        
        # 1. القائمة الرئيسية للتنقل
        render_main_menu()
        
        st.markdown("---")
        
        # 2. إعدادات المسح
        render_scan_settings()
        
        st.markdown("---")
        
        # 3. معلومات النظام والوقت
        render_system_info()
        
        return st.session_state.get('sidebar_config', {})

def render_main_menu():
    """عرض القائمة الرئيسية للتنقل بين الصفحات"""
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 مسح السوق": "scanner",
        "📈 تحليل سهم": "analyze",
        "📊 بيانات السوق": "market_data"
    }
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # العثور على الفهرس الحالي
    current_index = 0
    for i, (key, value) in enumerate(pages.items()):
        if value == current_page:
            current_index = i
            break
            
    selected = st.radio(
        "القائمة الرئيسية", 
        list(pages.keys()), 
        index=current_index,
        key="main_menu_radio"
    )
    
    new_page = pages[selected]
    if new_page != current_page:
        st.session_state.current_page = new_page
        st.rerun()

def render_scan_settings():
    """عرض شريط إعدادات الفحص والتصفية"""
    st.subheader("⚙️ إعدادات المسح")
    
    if 'sidebar_config' not in st.session_state:
        st.session_state.sidebar_config = {}
        
    config = st.session_state.sidebar_config
    
    min_score = st.slider(
        "🎯 درجة الجاهزية الأدنى", 
        40, 90, 
        config.get('min_score', 60),
        step=5,
        key="min_score_slider"
    )
    
    max_symbols = st.slider(
        "📈 عدد الأسهم للمسح",
        5, 30, 
        config.get('max_symbols', 15),
        step=5,
        key="max_symbols_slider"
    )
    
    scan_clicked = st.button(
        "🔍 ابدأ المسح", 
        use_container_width=True,
        type="primary",
        key="scan_button"
    )
    
    # حفظ الإعدادات في Session State
    st.session_state.sidebar_config = {
        'min_score': min_score,
        'max_symbols': max_symbols,
        'scan_clicked': scan_clicked
    }

def render_system_info():
    """عرض معلومات النظام والتوقيت"""
    if st.session_state.get('last_scan_time'):
        st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
    
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("💡 بيانات السوق محدثة")
    st.caption("🏷️ الإصدار: v2.0.0")
