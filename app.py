
2. تأكد من أن ملف `__init__.py` يحتوي على الاستيرادات الصحيحة

3. أعد تشغيل التطبيق
""")

if st.button("🔄 محاولة إعادة تحميل المحرك", type="primary"):
 st.rerun()

return

if not OPPORTUNITY_PAGE_AVAILABLE:
st.error("❌ **صفحة الفرص غير متوفرة**")
st.info("""
**لتفعيل صفحة الفرص:**

1. تأكد من وجود ملف `frontend/pages/opportunity_timeline.py`
2. تأكد من أن الملف يحتوي على دالة `main()`
3. أعد تشغيل التطبيق
""")
return

# ✅ كل شيء جاهز - عرض صفحة الفرص
try:
opportunity_page()
except Exception as e:
st.error(f"❌ حدث خطأ في صفحة الفرص: {str(e)}")
st.exception(e)

# ============================================================================
# 12. عرض الصفحة المختارة
# ============================================================================

def render_current_page():
"""عرض الصفحة المختارة"""
page = st.session_state.get('current_page', 'dashboard')

pages = {
'dashboard': render_dashboard,
'scanner': render_scanner,
'analyze': render_analyze,
'market_data': render_market_data,
'opportunity': render_opportunity_page,
}

pages.get(page, render_dashboard)()

# ============================================================================
# 13. التطبيق الرئيسي
# ============================================================================

def main():
"""الدالة الرئيسية"""

init_session_state()
load_css()

st.markdown("""
<div class="main-header">
<h1>🚀 AI Breakout Scanner</h1>
<p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي ومؤشرات الضغط (Squeeze)</p>
</div>
""", unsafe_allow_html=True)

render_sidebar()
render_current_page()

if __name__ == "__main__":
main()
