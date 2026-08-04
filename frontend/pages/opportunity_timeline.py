"""
صفحة التسلسل الزمني للفرص الاستثمارية
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional

# إضافة المسار
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.opportunity import (
    OpportunityEngine, MarketPhase, OpportunityResult,
    TimelineBuilder, PHASE_PROPERTIES
)


def init_page():
    """تهيئة الصفحة"""
    st.set_page_config(
        page_title="AI Opportunity Timeline",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_phase_badge(phase: MarketPhase):
    """عرض شارة المرحلة"""
    props = PHASE_PROPERTIES.get(phase, {})
    color = props.get('color', '#95a5a6')
    emoji = props.get('emoji', '📊')
    
    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            background-color: {color}22;
            border: 2px solid {color};
            color: {color};
            font-weight: bold;
            font-size: 14px;
        ">
            {emoji} {phase.value.replace('_', ' ').title()}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_score_bar(score: float, label: str = ""):
    """عرض شريط التقدم للدرجة"""
    filled = int(score / 10)
    empty = 10 - filled
    
    color = "green" if score >= 75 else "orange" if score >= 50 else "red"
    
    st.markdown(
        f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #666;">
                <span>{label}</span>
                <span style="color: {color}; font-weight: bold;">{score:.1f}%</span>
            </div>
            <div style="
                width: 100%;
                height: 12px;
                background: #f0f0f0;
                border-radius: 6px;
                overflow: hidden;
                margin-top: 3px;
            ">
                <div style="
                    width: {score}%;
                    height: 100%;
                    background: {color};
                    border-radius: 6px;
                    transition: width 0.5s;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_timeline(events, current_phase: MarketPhase):
    """عرض التسلسل الزمني باستخدام Plotly"""
    phases = []
    dates = []
    colors = []
    confidences = []
    
    for event in events:
        phases.append(event.phase.value.replace('_', ' ').title())
        dates.append(event.date)
        props = PHASE_PROPERTIES.get(event.phase, {})
        colors.append(props.get('color', '#95a5a6'))
        confidences.append(event.confidence * 100)
    
    fig = go.Figure()
    
    # خط التسلسل الزمني
    fig.add_trace(go.Scatter(
        x=dates,
        y=[1] * len(dates),
        mode='markers+lines',
        marker=dict(
            size=[20 + c/10 for c in confidences],
            color=colors,
            symbol='circle',
            line=dict(width=2, color='white')
        ),
        line=dict(color='#666', width=2),
        text=[f"{p}<br>الثقة: {c:.1f}%" for p, c in zip(phases, confidences)],
        hoverinfo='text',
        showlegend=False
    ))
    
    # إضافة تسميات
    for i, (date, phase, color, conf) in enumerate(zip(dates, phases, colors, confidences)):
        fig.add_annotation(
            x=date,
            y=1.15,
            text=phase,
            showarrow=False,
            font=dict(size=12, color=color),
            align='center'
        )
        
        fig.add_annotation(
            x=date,
            y=0.85,
            text=f"الثقة: {conf:.0f}%",
            showarrow=False,
            font=dict(size=10, color='#666'),
            align='center'
        )
    
    # تنسيق الرسم
    fig.update_layout(
        title="التسلسل الزمني للمراحل",
        xaxis_title="التاريخ",
        yaxis=dict(
            showticklabels=False,
            range=[0.7, 1.3],
            showgrid=False
        ),
        height=400,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_opportunity_phases(result: OpportunityResult):
    """عرض مراحل الفرصة"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 المرحلة الحالية")
        render_phase_badge(result.current_phase)
        st.metric("المدة", f"{result.current_phase_days} يوماً")
        st.metric("الثقة", f"{result.confidence:.1f}%")
    
    with col2:
        st.subheader("➡️ المرحلة القادمة")
        if result.next_phase:
            render_phase_badge(result.next_phase)
            st.metric("احتمال الانتقال", f"{result.transition_probability*100:.1f}%")
            st.metric("الأيام المتوقعة", f"{result.expected_days} أيام" if result.expected_days else "غير محدد")
        else:
            st.warning("لا توجد مرحلة تالية محددة")
    
    with col3:
        st.subheader("🎯 التقييم")
        st.metric("درجة الفرصة", f"{result.opportunity_score:.1f}%")
        st.metric("المستوى", result.score_level.value.replace('_', ' ').title())
        render_score_bar(result.opportunity_score, "")


def render_catalysts(result: OpportunityResult):
    """عرض المحفزات"""
    st.subheader("🔍 المحفزات")
    
    if result.catalysts:
        cols = st.columns(2)
        half = len(result.catalysts) // 2
        
        for i, catalyst in enumerate(result.catalysts):
            col = cols[i % 2]
            col.markdown(f"- {catalyst}")
    else:
        st.info("لم يتم رصد محفزات واضحة حالياً")


def render_ai_report(result: OpportunityResult):
    """عرض تقرير AI"""
    st.subheader("🤖 تقرير AI")
    
    with st.expander("📄 عرض التقرير الكامل", expanded=True):
        st.markdown(result.ai_decision_report)


def main():
    """الصفحة الرئيسية"""
    init_page()
    
    st.title("🚀 AI Opportunity Timeline")
    st.caption("تحليل الفرص الاستثمارية المتقدم باستخدام الذكاء الاصطناعي")
    
    # شريط جانبي
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        
        symbol = st.text_input("رمز السهم", value="AAPL").upper()
        
        st.divider()
        
        st.subheader("📊 المرشحات")
        show_catalysts = st.checkbox("عرض المحفزات", value=True)
        show_timeline = st.checkbox("عرض التسلسل الزمني", value=True)
        show_report = st.checkbox("عرض تقرير AI", value=True)
        
        st.divider()
        
        if st.button("🔄 تحديث التحليل", type="primary", use_container_width=True):
            st.rerun()
    
    if not symbol:
        st.warning("الرجاء إدخال رمز السهم")
        return
    
    try:
        # تهيئة المحرك
        engine = OpportunityEngine()
        timeline_builder = TimelineBuilder()
        
        # بيانات محاكاة (في الواقع ستأتي من مصادر حقيقية)
        data = {
            'bollinger_width': 0.27,
            'atr_ratio': 0.35,
            'volume_trend': 2.4,
            'trend_strength': 0.75,
            'rsi': 62,
            'smart_money_flow': 0.68,
            'pattern_score': 0.82,
            'sector_strength': 0.64,
            'market_regime': 0.58,
            'news_sentiment': 0.72,
            'volatility': 0.28,
            'price_trend': 0.045,
            'resistance_break': 1.035,
        }
        
        # تحليل الفرصة
        with st.spinner("جاري تحليل الفرصة..."):
            result = engine.analyze(symbol, data)
        
        # عرض النتائج
        st.divider()
        
        # العرض الرئيسي
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # عرض المراحل
            render_opportunity_phases(result)
        
        with col2:
            # عرض معلومات إضافية
            st.metric("عدد المحفزات", len(result.catalysts))
            st.metric("عدد المخاطر", len(result.risks))
        
        st.divider()
        
        # التسلسل الزمني
        if show_timeline:
            events = timeline_builder.build_timeline(
                result.current_phase,
                result.next_phase,
                result.current_phase_days,
                result.expected_days,
                data
            )
            render_timeline(events, result.current_phase)
            st.divider()
        
        # المحفزات
        if show_catalysts:
            render_catalysts(result)
            st.divider()
        
        # المخاطر
        if result.risks:
            st.subheader("⚠️ المخاطر المحتملة")
            for risk in result.risks:
                st.warning(risk)
            st.divider()
        
        # الأسباب
        if result.reasons:
            st.subheader("📋 أسباب التقييم")
            for reason in result.reasons:
                st.markdown(f"- {reason}")
            st.divider()
        
        # تقرير AI
        if show_report:
            render_ai_report(result)
        
        # تذييل
        st.divider()
        st.caption(f"⏰ آخر تحديث: {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء التحليل: {str(e)}")


if __name__ == "__main__":
    main()
