"""
مكون الشريط الجانبي (Sidebar) - AI Breakout Scanner
"""

import streamlit as st
from datetime import datetime

def render_sidebar():
    """عرض الشريط الجانبي الرئيسي وإرجاع الإعدادات"""
    with st.sidebar:
        # الشعار والعنوان
        st.image("https://img.icons8.com/fluency/96/stock.png", width=70)
        st.title("🤖 AI Scanner")
        st.markdown("---")
        
        # 1. القائمة الرئيسية للتنقل
        render_main_menu()
        
        st.markdown("---")
        
        # 2. إعدادات المسح الفني
        render_scan_settings()
        
        st.markdown("---")
        
        # 3. معلومات وتوقيت النظام
        render_system_info()
        
        # إرجاع إعدادات المسح لاستخدامها في باقي أجزاء التطبيق
        return st.session_state.get('sidebar_config', {})


def render_main_menu():
    """عرض القائمة الرئيسية للتنقل بين الصفحات"""
    st.subheader("📍 التنقل")
    
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 مسح السوق": "scanner",
        "📈 تحليل سهم": "analyze",
        "🌐 بيانات السوق": "market_data"  # الصفحة الجديدة
    }
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # تحديد الفهرس الحالي لمنع حدوث خطأ Indexing
    current_index = 0
    for i, (key, value) in enumerate(pages.items()):
        if value == current_page:
            current_index = i
            break
    
    selected_label = st.radio(
        "اختر الصفحة:", 
        list(pages.keys()), 
        index=current_index,
        key="main_menu_radio",
        label_visibility="collapsed"
    )
    
    selected_page_key = pages[selected_label]
    
    # تحديث الصفحة وإعادة التشغيل عند التغيير
    if selected_page_key != current_page:
        st.session_state.current_page = selected_page_key
        st.rerun()


def render_scan_settings():
    """عرض إعدادات وتخصيصات المسح"""
    st.subheader("⚙️ إعدادات المسح")
    
    if 'sidebar_config' not in st.session_state:
        st.session_state.sidebar_config = {}
        
    config = st.session_state.sidebar_config
    
    min_score = st.slider(
        "🎯 درجة الجاهزية الأدنى", 
        min_value=40, 
        max_value=90, 
        value=config.get('min_score', 60),
        step=5,
        key="min_score_slider"
    )
    
    max_symbols = st.slider(
        "📈 عدد الأسهم المستهدفة",
        min_value=5, 
        max_value=50, 
        value=config.get('max_symbols', 15),
        step=5,
        key="max_symbols_slider"
    )
    
    scan_clicked = st.button(
        "🔍 ابدأ المسح الآن", 
        type="primary",
        use_container_width=True,
        key="scan_button"
    )
    
    # حفظ الإعدادات في Session State
    st.session_state.sidebar_config = {
        'min_score': min_score,
        'max_symbols': max_symbols,
        'scan_clicked': scan_clicked
    }


def render_system_info():
    """عرض معلومات النظام والحالة"""
    if st.session_state.get('last_scan_time'):
        st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    st.caption(f"🕐 {current_time}")
    st.caption("💡 النسخة v2.0.0 | البيانات محدثة")
