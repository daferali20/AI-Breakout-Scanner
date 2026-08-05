"""
🚀 AI Opportunity Timeline
صفحة التسلسل الزمني للفرص الاستثمارية - الإصدار المتكامل
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# إضافة مسار backend إلى sys.path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

# استيراد وحدات الفرص (تأكد من وجود المجلد والوحدات)
try:
    from opportunity import (
        INDICATOR_WEIGHTS,
        PHASE_PROPERTIES,
        Catalysts,
        MarketPhase,
        OpportunityEngine,
        OpportunityResult,
        OpportunityScoreLevel,
        TimelineBuilder,
    )
except ImportError:
    st.error("❌ تعذر استيراد وحدة backend/opportunity. تأكد من صحة مسار الملفات.")


# ============================================================
# دوال العرض المساعدة
# ============================================================

def render_phase_badge(phase: Any, size: str = "normal"):
    """عرض شارة المرحلة مع لون وأيقونة"""
    props = PHASE_PROPERTIES.get(phase, {})
    color = props.get('color', '#95a5a6')
    emoji = props.get('emoji', '📊')
    description = props.get('description', str(phase.value).replace('_', ' ').title())
    
    font_size = "16px" if size == "large" else "14px"
    padding = "8px 20px" if size == "large" else "5px 15px"
    
    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: {padding};
            border-radius: 20px;
            background-color: {color}22;
            border: 2px solid {color};
            color: {color};
            font-weight: bold;
            font-size: {font_size};
            margin: 2px 0;
        ">
            {emoji} {description}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_score_bar(score: float, label: str = "", height: int = 12, show_percent: bool = True):
    """عرض شريط التقدم للدرجة"""
    score = max(0.0, min(100.0, float(score)))
    
    if score >= 75:
        color = "#2ecc71"  # أخضر
    elif score >= 50:
        color = "#f39c12"  # برتقالي
    elif score >= 30:
        color = "#e67e22"  # برتقالي غامق
    else:
        color = "#e74c3c"  # أحمر
    
    percent_text = f"{score:.1f}%" if show_percent else ""
    
    st.markdown(
        f"""
        <div style="margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; color: #666; margin-bottom: 3px;">
                <span>{label}</span>
                <span style="color: {color}; font-weight: bold;">{percent_text}</span>
            </div>
            <div style="
                width: 100%;
                height: {height}px;
                background: #f0f0f0;
                border-radius: 6px;
                overflow: hidden;
            ">
                <div style="
                    width: {score}%;
                    height: 100%;
                    background: linear-gradient(90deg, {color}88, {color});
                    border-radius: 6px;
                    transition: width 0.8s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title: str, value: str, delta: Optional[str] = None, 
                       icon: str = "📊", color: str = "#3498db"):
    """عرض بطاقة مقياس بتنسيق جميل"""
    delta_html = f'<span style="color: {color}; font-size: 14px;">{delta}</span>' if delta else ''
    
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 4px solid {color};
            margin: 5px 0;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 28px;">{icon}</span>
                <div>
                    <div style="font-size: 13px; color: #888; font-weight: 500;">{title}</div>
                    <div style="font-size: 22px; font-weight: 700; color: #1a1a2e;">
                        {value} {delta_html}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# دوال عرض البيانات الرئيسية
# ============================================================

def render_opportunity_overview(result: Any):
    """عرض نظرة عامة على الفرصة"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "المرحلة الحالية",
            result.current_phase.value.replace('_', ' ').title(),
            icon=PHASE_PROPERTIES.get(result.current_phase, {}).get('emoji', '📊'),
            color=PHASE_PROPERTIES.get(result.current_phase, {}).get('color', '#3498db')
        )
    
    with col2:
        render_metric_card(
            "المدة في المرحلة",
            f"{result.current_phase_days} يوم",
            delta=f"ثقة {result.confidence:.0f}%",
            icon="📅",
            color="#2ecc71"
        )
    
    with col3:
        if result.next_phase:
            next_emoji = PHASE_PROPERTIES.get(result.next_phase, {}).get('emoji', '➡️')
            render_metric_card(
                "المرحلة القادمة",
                result.next_phase.value.replace('_', ' ').title(),
                delta=f"احتمال {result.transition_probability*100:.0f}%",
                icon=next_emoji,
                color=PHASE_PROPERTIES.get(result.next_phase, {}).get('color', '#9b59b6')
            )
        else:
            render_metric_card(
                "المرحلة القادمة",
                "غير محدد",
                icon="❓",
                color="#95a5a6"
            )
    
    with col4:
        score_emoji = "🌟" if result.opportunity_score >= 75 else "📈" if result.opportunity_score >= 50 else "⚠️"
        render_metric_card(
            "درجة الفرصة",
            f"{result.opportunity_score:.1f}%",
            delta=result.score_level.value.replace('_', ' ').title(),
            icon=score_emoji,
            color="#e74c3c" if result.opportunity_score < 40 else "#f39c12" if result.opportunity_score < 60 else "#2ecc71"
        )


def render_timeline_chart(events: List, current_phase: Any):
    """عرض التسلسل الزمني التفاعلي باستخدام Plotly"""
    if not events:
        st.info("لا توجد بيانات كافية لعرض التسلسل الزمني")
        return
    
    # تجهيز البيانات
    phases, dates, colors, confidences, descriptions = [], [], [], [], []
    
    for event in events:
        phase_name = event.phase.value.replace('_', ' ').title()
        phases.append(phase_name)
        dates.append(event.date)
        props = PHASE_PROPERTIES.get(event.phase, {})
        colors.append(props.get('color', '#95a5a6'))
        confidences.append(float(event.confidence) * 100)
        descriptions.append(props.get('description', phase_name))
    
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3]
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode='markers+lines',
            marker=dict(
                size=[30 + (c / 5) for c in confidences],
                color=colors,
                symbol='circle',
                line=dict(width=3, color='white')
            ),
            line=dict(color='#bdc3c7', width=3),
            text=[f"<b>{p}</b><br>{d}<br>الثقة: {c:.0f}%" for p, d, c in zip(phases, descriptions, confidences)],
            hoverinfo='text',
            name='المراحل'
        ),
        row=1, col=1
    )
    
    for date, phase, color, conf in zip(dates, phases, colors, confidences):
        fig.add_annotation(
            x=date, y=1.12,
            text=phase,
            showarrow=False,
            font=dict(size=11, color=color, weight='bold'),
            align='center', row=1, col=1
        )
        fig.add_annotation(
            x=date, y=0.88,
            text=f"{conf:.0f}%",
            showarrow=False,
            font=dict(size=9, color='#7f8c8d'),
            align='center', row=1, col=1
        )
    
    fig.add_trace(
        go.Bar(
            x=dates,
            y=confidences,
            marker=dict(color=colors, line=dict(width=1, color='white')),
            text=[f"{c:.0f}%" for c in confidences],
            textposition='outside',
            name='الثقة',
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=dict(text="📅 التسلسل الزمني للمراحل", font=dict(size=18, weight='bold'), x=0.5),
        height=450,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=60, b=30),
        showlegend=False,
    )
    
    fig.update_xaxes(title_text="التاريخ", gridcolor='#ecf0f1', row=2, col=1)
    fig.update_yaxes(range=[0.7, 1.3], showticklabels=False, showgrid=False, row=1, col=1)
    fig.update_yaxes(title_text="الثقة %", range=[0, 110], gridcolor='#ecf0f1', row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def render_phase_indicators(result: Any, data: Dict[str, Any]):
    """عرض المؤشرات الفنية للمرحلة"""
    st.subheader("📊 مؤشرات المرحلة")
    cols = st.columns(4)
    
    indicators = [
        ('📈 Smart Money', data.get('smart_money_flow', 0), 0.20),
        ('📊 الحجم النسبي', data.get('relative_volume', 0), 0.15),
        ('📉 Bollinger Squeeze', data.get('bollinger_squeeze', 0), 0.12),
        ('📉 ATR Compression', data.get('atr_compression', 0), 0.10),
        ('🎯 Pattern Detection', data.get('pattern_detection', 0), 0.12),
        ('🏭 Sector Strength', data.get('sector_strength', 0), 0.08),
        ('🌍 Market Regime', data.get('market_regime', 0), 0.08),
        ('📰 News Sentiment', data.get('news_sentiment', 0), 0.05),
        ('💵 Earnings', data.get('earnings', 0), 0.05),
        ('🤖 AI Score', data.get('ai_score', 0), 0.05),
    ]
    
    for i, (name, value, weight) in enumerate(indicators):
        col = cols[i % 4]
        with col:
            if isinstance(value, (int, float)):
                display_value = min(100.0, max(0.0, float(value) * 100))
                color = "#2ecc71" if display_value >= 70 else "#f39c12" if display_value >= 40 else "#e74c3c"
                
                st.markdown(
                    f"""
                    <div style="
                        background: #f8f9fa;
                        border-radius: 10px;
                        padding: 12px 15px;
                        margin: 5px 0;
                        border-left: 3px solid {color};
                    ">
                        <div style="font-size: 12px; color: #888; font-weight: 500;">{name}</div>
                        <div style="font-size: 18px; font-weight: 700; color: {color};">
                            {display_value:.1f}%
                        </div>
                        <div style="font-size: 10px; color: #aaa;">وزن: {weight*100:.0f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def render_catalysts(catalysts: List[str]):
    """عرض المحفزات"""
    st.subheader("🔍 المحفزات")
    if not catalysts:
        st.info("لم يتم رصد محفزات واضحة حالياً")
        return
    
    cols = st.columns(2)
    for i, catalyst in enumerate(catalysts):
        col = cols[i % 2]
        with col:
            st.markdown(
                f"""
                <div style="
                    background: #f0f7ff;
                    border-radius: 8px;
                    padding: 10px 15px;
                    margin: 4px 0;
                    border: 1px solid #d6e9ff;
                    font-size: 14px;
                ">
                    {catalyst}
                </div>
                """,
                unsafe_allow_html=True
            )


def render_risks(risks: List[str]):
    """عرض المخاطر"""
    if not risks:
        return
    st.subheader("⚠️ المخاطر المحتملة")
    for risk in risks:
        st.warning(risk)


def render_reasons(reasons: List[str]):
    """عرض أسباب التقييم"""
    if not reasons:
        return
    st.subheader("📋 أسباب التقييم")
    for reason in reasons:
        st.markdown(f"- {reason}")


def render_ai_report(result: Any):
    """عرض تقرير AI الكامل"""
    st.subheader("🤖 تقرير AI الشامل")
    with st.expander("📄 عرض التقرير الكامل", expanded=False):
        st.markdown(getattr(result, 'ai_decision_report', 'لا يوجد تقرير كافي.'))


def render_opportunity_score_breakdown(result: Any):
    """عرض تفصيل درجة الفرصة"""
    st.subheader("🎯 تفصيل درجة الفرصة")
    render_score_bar(result.opportunity_score, "الدرجة الإجمالية", height=20)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**مكونات التقييم**")
        st.caption("جودة المرحلة")
        render_score_bar(85, "", height=8)
        st.caption("المحفزات")
        render_score_bar(70 + min(30, len(result.catalysts) * 4), "", height=8)
        
    with col2:
        st.markdown("**مكونات التقييم**")
        st.caption("احتمال الانتقال")
        render_score_bar(result.transition_probability * 100, "", height=8)
        st.caption("الثقة")
        render_score_bar(result.confidence, "", height=8)
        
    with col3:
        st.markdown("**مكونات التقييم**")
        st.caption("الزخم")
        render_score_bar(65 + min(35, result.opportunity_score * 0.3), "", height=8)


# ============================================================
# الصفحة الرئيسية
# ============================================================

def main():
    """الصفحة الرئيسية لتسلسل الفرص"""
    st.set_page_config(
        page_title="🚀 AI Opportunity Timeline",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 AI Opportunity Timeline")
    st.caption("تحليل الفرص الاستثمارية المتقدم باستخدام الذكاء الاصطناعي")
    st.divider()
    
    # ===== الشريط الجانبي =====
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        symbol = st.text_input("🔍 رمز السهم", value="AAPL", help="أدخل رمز السهم المراد تحليله").upper()
        
        st.divider()
        st.subheader("📊 خيارات العرض")
        show_indicators = st.checkbox("مؤشرات المرحلة", value=True)
        show_catalysts = st.checkbox("المحفزات", value=True)
        show_risks = st.checkbox("المخاطر", value=True)
        show_reasons = st.checkbox("أسباب التقييم", value=True)
        show_timeline = st.checkbox("التسلسل الزمني", value=True)
        show_score_breakdown = st.checkbox("تفصيل الدرجة", value=True)
        show_report = st.checkbox("تقرير AI", value=False)
        
        st.divider()
        if st.button("🔄 تحديث التحليل", type="primary", use_container_width=True):
            st.rerun()
            
        st.divider()
        st.caption(f"⏰ آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")
    
    if not symbol:
        st.warning("⚠️ الرجاء إدخال رمز السهم")
        return
    
    # ===== التحليل =====
    try:
        engine = OpportunityEngine()
        timeline_builder = TimelineBuilder()
        
        analysis_data = {
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
            'support_hold': 0.985,
            'volume_spike': 2.8,
            'ai_score': 0.88,
            'earnings': 0.55,
            'relative_volume': 2.4,
            'bollinger_squeeze': 0.73,
            'atr_compression': 0.65,
            'pattern_detection': 0.82,
        }
        
        with st.spinner(f"🔄 جاري تحليل {symbol}..."):
            result = engine.analyze(symbol, analysis_data)
        
        # ===== عرض النتائج =====
        render_opportunity_overview(result)
        st.divider()
        
        render_score_bar(result.opportunity_score, "🎯 درجة الفرصة الإجمالية", height=16)
        st.divider()
        
        if show_timeline:
            events = timeline_builder.build_timeline(
                result.current_phase,
                result.next_phase,
                result.current_phase_days,
                result.expected_days,
                analysis_data
            )
            render_timeline_chart(events, result.current_phase)
            st.divider()
        
        if show_indicators:
            render_phase_indicators(result, analysis_data)
            st.divider()
        
        if show_score_breakdown:
            render_opportunity_score_breakdown(result)
            st.divider()
        
        if show_catalysts and getattr(result, 'catalysts', None):
            render_catalysts(result.catalysts)
            st.divider()
        
        if show_risks and getattr(result, 'risks', None):
            render_risks(result.risks)
            st.divider()
        
        if show_reasons and getattr(result, 'reasons', None):
            render_reasons(result.reasons)
            st.divider()
        
        if show_report:
            render_ai_report(result)
            st.divider()
        
        with st.expander("📊 بيانات التحليل الخام", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.json({
                    'symbol': result.symbol,
                    'current_phase': result.current_phase.value,
                    'confidence': result.confidence,
                    'opportunity_score': result.opportunity_score,
                    'score_level': result.score_level.value,
                    'transition_probability': result.transition_probability,
                })
            with col2:
                st.json({
                    'phase_days': result.current_phase_days,
                    'expected_days': result.expected_days,
                    'catalysts_count': len(getattr(result, 'catalysts', [])),
                    'risks_count': len(getattr(result, 'risks', [])),
                    'analysis_time': result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                })
        
        st.divider()
        st.caption(f"✅ تم التحليل بنجاح | {symbol} | {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء التحليل: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
