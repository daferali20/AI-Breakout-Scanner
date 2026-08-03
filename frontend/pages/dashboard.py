# frontend/pages/dashboard.py
"""
صفحة لوحة التحكم الرئيسية - نسخة محسنة وديناميكية
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


def render():
    """عرض لوحة التحكم الرئيسية"""
    # عنوان الصفحة مع وقت التحديث
    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.subheader("📊 لوحة التحكم - نظرة عامة على السوق")
    with col_time:
        last_scan = st.session_state.get('last_scan_time', 'لم يتم')
        st.caption(f"🕐 آخر تحديث: {last_scan}")
    
    # عرض بطاقات الإحصائيات الديناميكية
    display_metrics()
    
    st.markdown("---")
    
    # عرض رسوم بيانية وتحليلات
    display_charts()
    
    st.markdown("---")
    
    # عرض نتائج المسح
    display_scan_results()


def display_metrics():
    """عرض بطاقات الإحصائيات الديناميكية"""
    # جلب البيانات من session state
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    # حساب الإحصائيات
    total_stocks = get_total_stocks_count()
    opportunities = len(results) if not results.empty else 0
    
    # حساب متوسط الدرجة
    avg_score = 0
    if not results.empty and 'score' in results.columns:
        avg_score = round(results['score'].mean(), 1)
    elif not results.empty and 'Score' in results.columns:
        avg_score = round(results['Score'].mean(), 1)
    
    # حساب عدد الإشارات القوية
    strong_signals = 0
    if not results.empty:
        if 'recommendation' in results.columns:
            strong_signals = len(results[results['recommendation'].str.contains('شراء قوي|BUY|قوي', case=False)])
        elif 'Signal' in results.columns:
            strong_signals = len(results[results['Signal'].str.contains('BUY|شراء', case=False)])
    
    # عرض البطاقات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="value">{total_stocks}</div>
            <div class="label">أسهم متاحة للتحليل</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = "#00E676" if opportunities > 0 else "#FF5252"
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:{color};">{opportunities}</div>
            <div class="label">فرص مكتشفة 🎯</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">⭐</div>
            <div class="value" style="color:#FFD700;">{avg_score}%</div>
            <div class="label">متوسط درجة الثقة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🚀</div>
            <div class="value" style="color:#29B6F6;">{strong_signals}</div>
            <div class="label">إشارات شراء قوية</div>
        </div>
        """, unsafe_allow_html=True)


def get_total_stocks_count():
    """حساب عدد الأسهم المتاحة"""
    try:
        from config import STOCK_SYMBOLS
        if isinstance(STOCK_SYMBOLS, dict):
            all_symbols = []
            for syms in STOCK_SYMBOLS.values():
                if isinstance(syms, list):
                    all_symbols.extend(syms)
            return len(set(all_symbols))
        elif isinstance(STOCK_SYMBOLS, list):
            return len(STOCK_SYMBOLS)
        else:
            return 150  # قيمة افتراضية
    except:
        return 150  # قيمة افتراضية


def display_charts():
    """عرض الرسوم البيانية والتحليلات"""
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    if results.empty:
        st.info("📊 قم بتشغيل المسح لعرض الرسوم البيانية")
        return
    
    # التحقق من وجود الأعمدة المطلوبة
    score_col = 'score' if 'score' in results.columns else 'Score' if 'Score' in results.columns else None
    symbol_col = 'symbol' if 'symbol' in results.columns else 'Symbol' if 'Symbol' in results.columns else None
    
    if not score_col or not symbol_col:
        st.warning("⚠️ البيانات غير مكتملة لعرض الرسوم البيانية")
        return
    
    # عمودين للرسوم البيانية
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 توزيع درجات الثقة")
        
        # تحضير البيانات
        chart_data = results[[symbol_col, score_col]].copy()
        chart_data.columns = ['الرمز', 'الدرجة']
        chart_data = chart_data.sort_values('الدرجة', ascending=False).head(15)
        
        # رسم بياني شريطي باستخدام Plotly
        fig = px.bar(
            chart_data,
            x='الرمز',
            y='الدرجة',
            title='أعلى 15 سهم حسب درجة الثقة',
            color='الدرجة',
            color_continuous_scale='Viridis',
            text='الدرجة'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 100])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 توزيع التوصيات")
        
        # تحليل التوصيات
        rec_col = 'recommendation' if 'recommendation' in results.columns else 'Signal' if 'Signal' in results.columns else None
        
        if rec_col:
            recommendations = results[rec_col].value_counts()
            
            fig = px.pie(
                values=recommendations.values,
                names=recommendations.index,
                title='توزيع التوصيات',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                legend=dict(font=dict(color='white'))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # عرض معلومات بديلة
            st.info("لا توجد بيانات توصيات للعرض")
            
            # عرض جدول بسيط
            st.dataframe(
                results[[symbol_col, score_col]].head(10),
                column_config={
                    symbol_col: "الرمز",
                    score_col: st.column_config.ProgressColumn("الدرجة", format="%.0f%%", min_value=0, max_value=100)
                },
                use_container_width=True
            )


def display_scan_results():
    """عرض نتائج المسح في جدول تفاعلي"""
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    if results.empty:
        st.info("🔍 اضغط 'بدء المسح' في الشريط الجانبي للبدء")
        return
    
    st.subheader("📋 أفضل الفرص المكتشفة")
    
    # تحديد الأعمدة المتاحة
    available_columns = {}
    column_mapping = {
        'symbol': 'الرمز',
        'Symbol': 'الرمز',
        'score': 'الدرجة',
        'Score': 'الدرجة',
        'squeeze': 'الانضغاط',
        'Squeeze': 'الانضغاط',
        'recommendation': 'التوصية',
        'Recommendation': 'التوصية',
        'Signal': 'الإشارة',
        'risk': 'المخاطرة',
        'Risk': 'المخاطرة',
        'Risk_Level': 'المخاطرة',
        'price': 'السعر',
        'Price': 'السعر',
        'target': 'الهدف',
        'Target': 'الهدف',
        'volume': 'الحجم',
        'Volume': 'الحجم'
    }
    
    # بناء قائمة الأعمدة للعرض
    display_cols = []
    for col in results.columns:
        if col in column_mapping:
            display_cols.append(column_mapping[col])
        else:
            display_cols.append(col)
    
    # إعادة تسمية الأعمدة
    display_df = results.copy()
    display_df.columns = display_cols
    
    # ترتيب الأعمدة المفضلة
    preferred_order = ['الرمز', 'السعر', 'الدرجة', 'الانضغاط', 'التوصية', 'الإشارة', 'المخاطرة', 'الهدف', 'الحجم']
    existing_cols = [col for col in preferred_order if col in display_df.columns]
    other_cols = [col for col in display_df.columns if col not in preferred_order]
    final_cols = existing_cols + other_cols
    
    display_df = display_df[final_cols]
    
    # عرض الجدول مع تنسيق متقدم
    st.dataframe(
        display_df,
        column_config={
            "الرمز": st.column_config.TextColumn("الرمز", width="small"),
            "السعر": st.column_config.NumberColumn("السعر", format="$%.2f"),
            "الهدف": st.column_config.NumberColumn("الهدف", format="$%.2f"),
            "الدرجة": st.column_config.ProgressColumn("الدرجة", format="%.0f/100", min_value=0, max_value=100),
            "الانضغاط": st.column_config.ProgressColumn("الانضغاط", format="%.0f%%", min_value=0, max_value=100),
            "التوصية": st.column_config.TextColumn("التوصية"),
            "الإشارة": st.column_config.TextColumn("الإشارة"),
            "المخاطرة": st.column_config.TextColumn("المخاطرة"),
            "الحجم": st.column_config.TextColumn("الحجم")
        },
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # أزرار إضافية
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # تصدير النتائج
        csv = results.to_csv(index=False)
        st.download_button(
            label="📥 تحميل CSV",
            data=csv,
            file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # تحديث البيانات
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.session_state.scan_in_progress = True
            st.rerun()
    
    with col3:
        # عرض إحصائيات سريعة
        if 'الدرجة' in display_df.columns:
            avg = display_df['الدرجة'].mean()
            max_score = display_df['الدرجة'].max()
            min_score = display_df['الدرجة'].min()
            st.caption(f"📊 متوسط الدرجة: {avg:.1f} | أعلى: {max_score:.0f} | أدنى: {min_score:.0f}")
