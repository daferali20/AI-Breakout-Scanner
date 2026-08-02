# frontend/pages/dashboard.py
"""
صفحة لوحة التحكم الرئيسية
"""

import streamlit as st
import pandas as pd

def render():
    """عرض لوحة التحكم"""
    st.subheader("📊 نظرة عامة")
    
    # بطاقات الإحصائيات
    display_metrics()
    
    st.markdown("---")
    
    # عرض نتائج المسح
    display_scan_results()

def display_metrics():
    """عرض بطاقات الإحصائيات"""
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

def display_scan_results():
    """عرض نتائج المسح"""
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    if not results.empty:
        st.subheader("📋 أفضل الفرص")
        st.dataframe(
            results,
            column_config={
                "symbol": st.column_config.TextColumn("الرمز", width="small"),
                "score": st.column_config.ProgressColumn("الدرجة", format="%.0f/100", min_value=0, max_value=100),
                "squeeze": st.column_config.ProgressColumn("الانضغاط", format="%.0f/100", min_value=0, max_value=100),
                "recommendation": st.column_config.TextColumn("التوصية"),
                "risk": st.column_config.TextColumn("المخاطرة"),
                "price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "target": st.column_config.NumberColumn("الهدف", format="$%.2f")
            },
            width='stretch',
            hide_index=True
        )
    else:
        st.info("🔍 اضغط 'بدء المسح' في الشريط الجانبي للبدء")
