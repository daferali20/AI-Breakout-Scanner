"""واجهة تسجيل الدخول وإنشاء الحساب باستخدام Supabase."""
from __future__ import annotations

import streamlit as st

from backend.supabase_auth import establish_session, sign_in, sign_up


def _login_form() -> None:
    st.subheader("🔐 تسجيل الدخول")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="name@example.com")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول", type="primary", width="stretch")

    if submitted:
        if not email or not password:
            st.warning("أدخل البريد الإلكتروني وكلمة المرور.")
            return
        try:
            payload = sign_in(email, password)
            establish_session(payload)
            st.success("تم تسجيل الدخول بنجاح.")
            st.rerun()
        except Exception as exc:
            st.error(f"تعذر تسجيل الدخول: {exc}")


def _signup_form() -> None:
    st.subheader("👤 إنشاء حساب مجاني")
    with st.form("signup_form"):
        full_name = st.text_input("الاسم الكامل")
        email = st.text_input("البريد الإلكتروني", placeholder="name@example.com", key="signup_email")
        password = st.text_input("كلمة المرور", type="password", key="signup_password")
        confirm = st.text_input("تأكيد كلمة المرور", type="password")
        submitted = st.form_submit_button("إنشاء الحساب", type="primary", width="stretch")

    if submitted:
        if not full_name or not email or not password:
            st.warning("أكمل الاسم والبريد وكلمة المرور.")
            return
        if len(password) < 6:
            st.warning("كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
            return
        if password != confirm:
            st.warning("كلمتا المرور غير متطابقتين.")
            return
        try:
            payload = sign_up(email, password, full_name)
            result = establish_session(payload)
            if result.get("requires_confirmation"):
                st.success("تم إنشاء الحساب. تحقق من بريدك الإلكتروني لتأكيد الحساب، ثم سجّل الدخول.")
            else:
                st.success("تم إنشاء الحساب وتسجيل الدخول بالخطة المجانية.")
                st.rerun()
        except Exception as exc:
            st.error(f"تعذر إنشاء الحساب: {exc}")


def render() -> None:
    st.markdown(
        """
        <div style="text-align:center;padding:28px 10px 18px;">
            <div style="font-size:13px;opacity:.7;letter-spacing:1px;">AI BREAKOUT SCANNER</div>
            <div style="font-size:38px;font-weight:800;margin-top:4px;">ابدأ من هنا</div>
            <div style="font-size:16px;opacity:.75;margin-top:8px;">أنشئ حسابًا مجانيًا أو سجّل الدخول للوصول إلى أدوات السوق.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2.4, 1])
    with center:
        tab_login, tab_signup = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab_login:
            _login_form()
        with tab_signup:
            _signup_form()

        st.caption("الحسابات الجديدة تبدأ تلقائيًا بالخطة المجانية. يتم تحديد الخطة من Supabase بعد تسجيل الدخول.")
