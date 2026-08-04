# AI-Breakout-Scanner/frontend/app.py

import streamlit as st
import sys
from pathlib import Path

# إضافة المسارات
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

# إعداد الصفحة
st.set_page_config(
    page_title="AI Breakout Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استيراد الصفحات
from pages.opportunity_timeline import main as opportunity_page


def main():
    """التطبيق الرئيسي"""
    
    # القائمة الجانبية
    with st.sidebar:
        st.title("🚀 AI Breakout Scanner")
        st.markdown("---")
        
        # القائمة الرئيسية
        page = st.radio(
            "📋 القائمة",
            [
                "🏠 لوحة التحكم",
                "🚀 AI Opportunity Timeline",
                "📊 الماسح الضوئي",
                "📈 التحليل الفني",
                "📰 تحليل الأخبار",
                "⚙️ الإعدادات",
            ],
            index=0
        )
        
        st.markdown("---")
        st.caption("v2.0 - AI Powered")
    
    # توجيه الصفحات
    if page == "🏠 لوحة التحكم":
        show_dashboard()
    elif page == "🚀 AI Opportunity Timeline":
        opportunity_page()  # الصفحة الجديدة
    elif page == "📊 الماسح الضوئي":
        show_scanner()
    elif page == "📈 التحليل الفني":
        show_technical()
    elif page == "📰 تحليل الأخبار":
        show_news()
    elif page == "⚙️ الإعدادات":
        show_settings()


def show_dashboard():
    """لوحة التحكم الرئيسية"""
    st.title("🏠 لوحة التحكم")
    st.markdown("مرحباً بك في مساعد كشف الاختراقات بالذكاء الاصطناعي")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 فرص نشطة", "12", delta="+3")
    with col2:
        st.metric("🎯 ثقة عالية", "87%", delta="+5%")
    with col3:
        st.metric("⚡ اختراقات متوقعة", "5", delta="+2")
    with col4:
        st.metric("📊 محفزات كلية", "23", delta="-1")
    
    st.divider()
    
    # عرض سريع للفرص
    st.subheader("🔍 أفضل الفرص الحالية")
    
    # بيانات تجريبية
    opportunities = [
        {"السهم": "AAPL", "المرحلة": "ضغط سيولة", "الفرصة": "94%", "الثقة": "88%"},
        {"السهم": "MSFT", "المرحلة": "جاهزية اختراق", "الفرصة": "89%", "الثقة": "92%"},
        {"السهم": "GOOGL", "المرحلة": "زخم", "الفرصة": "81%", "الثقة": "76%"},
        {"السهم": "AMZN", "المرحلة": "تجميع", "الفرصة": "76%", "الثقة": "71%"},
    ]
    
    for opp in opportunities:
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: space-between;
                padding: 10px 15px;
                background: #f8f9fa;
                border-radius: 8px;
                margin: 4px 0;
                border-left: 4px solid {'#2ecc71' if int(opp['الفرصة'].replace('%', '')) > 80 else '#f39c12'};
            ">
                <span style="font-weight: 600;">{opp['السهم']}</span>
                <span>{opp['المرحلة']}</span>
                <span style="color: {'#2ecc71' if int(opp['الفرصة'].replace('%', '')) > 80 else '#f39c12'};">
                    الفرصة: {opp['الفرصة']}
                </span>
                <span>الثقة: {opp['الثقة']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.info("🚀 اضغط على 'AI Opportunity Timeline' في القائمة الجانبية للتحليل المتقدم")


def show_scanner():
    st.title("📊 الماسح الضوئي")
    st.info("🔍 صفحة الماسح الضوئي - قيد التطوير")


def show_technical():
    st.title("📈 التحليل الفني")
    st.info("📊 صفحة التحليل الفني - قيد التطوير")


def show_news():
    st.title("📰 تحليل الأخبار")
    st.info("📰 صفحة تحليل الأخبار - قيد التطوير")


def show_settings():
    st.title("⚙️ الإعدادات")
    st.info("⚙️ صفحة الإعدادات - قيد التطوير")


if __name__ == "__main__":
    main()
