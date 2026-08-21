"""واجهة اختيار الخطة قبل الدخول إلى التطبيق."""
from __future__ import annotations
import streamlit as st


def render() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding:2.2rem 0 1rem 0;">
            <div style="font-size:3.2rem;">🚀</div>
            <h1 style="margin-bottom:.35rem;">AI Breakout Scanner</h1>
            <p style="font-size:1.15rem; opacity:.78; max-width:760px; margin:auto;">
                منصة ذكية لاكتشاف الأسهم القوية، قراءة الزخم والسيولة، وترتيب الفرص بطريقة واضحة وسريعة.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### اختر الخطة المناسبة")
    free_col, pro_col = st.columns(2, gap="large")

    with free_col:
        with st.container(border=True):
            st.markdown("## 🟢 الخطة المجانية")
            st.markdown("### $0")
            st.caption("ابدأ بمراقبة السوق وتجربة أدوات المنصة الأساسية.")
            st.markdown(
                """
                - 🏠 لوحة تحكم مبسطة
                - 🔎 مستكشف السوق الأساسي
                - 📊 تحليل سهم فردي
                - 🚀 مشاهدة الأسهم الأكثر ارتفاعًا
                - 💵 نطاقات سعرية وفلاتر أساسية
                - ⚡ قراءة أولية للزخم والسيولة
                """
            )
            if st.button("ابدأ مجانًا", type="primary", width="stretch", key="choose_free_plan"):
                st.session_state.plan_selected = "free"
                st.session_state.active_page = "free_home"
                st.rerun()

    with pro_col:
        with st.container(border=True):
            st.markdown("## 👑 الخطة المدفوعة")
            st.markdown("### Pro")
            st.caption("سنفعّلها بعد إكمال تجربة الخطة المجانية.")
            st.markdown(
                """
                - 🧠 Opportunity Intelligence الكامل
                - ⭐ قائمة المراقبة الذكية
                - 🔔 التنبيهات المتقدمة
                - 💧 تحليل السيولة والزخم المتقدم
                - 📚 سجل الفرص المستخرجة سابقًا
                - 📰 المحفزات والإشارات المتقدمة
                """
            )
            st.button("قريبًا", disabled=True, width="stretch", key="pro_coming_soon")

    st.markdown("---")
    a, b, c = st.columns(3)
    a.markdown("**⚡ سرعة**\n\nاكتشاف أهم تحركات السوق من واجهة واحدة.")
    b.markdown("**🧠 ذكاء**\n\nتقييم الفرص بدل عرض الأسعار فقط.")
    c.markdown("**💧 سيولة**\n\nفهم ما إذا كان الصعود مدعومًا بحجم وتدفق فعلي.")
