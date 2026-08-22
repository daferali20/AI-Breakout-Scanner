"""واجهة تسجيل الدخول وإنشاء الحساب باستخدام Supabase."""
from __future__ import annotations

import streamlit as st
from supabase_auth import establish_session, request_password_reset, sign_in, sign_up


def _forgot_password_form() -> None:
    with st.expander("🔑 نسيت كلمة المرور؟", expanded=False):
        st.caption("أدخل بريدك الإلكتروني وسيرسل النظام رابط إعادة ضبط كلمة المرور.")
        with st.form("forgot_password_form"):
            email = st.text_input("البريد الإلكتروني", placeholder="name@example.com", key="reset_email")
            submitted = st.form_submit_button("إرسال رابط إعادة الضبط", width="stretch")
        if submitted:
            if not email:
                st.warning("أدخل البريد الإلكتروني.")
                return
            try:
                request_password_reset(email)
            except Exception:
                pass
            st.success("إذا كان البريد مسجلًا، فسيصله رابط إعادة ضبط كلمة المرور.")
            st.caption("تحقق من صندوق الوارد والرسائل غير المرغوب فيها.")


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
            st.session_state.guest_mode = False
            st.success("تم تسجيل الدخول بنجاح.")
            st.rerun()
        except Exception:
            st.error("تعذر تسجيل الدخول. تحقق من البريد الإلكتروني وكلمة المرور ثم حاول مرة أخرى.")
    _forgot_password_form()


def _signup_form() -> None:
    st.subheader("🎁 إنشاء حساب + تجربة Pro لمدة 7 أيام")
    st.info("الحساب الجديد يحصل تلقائيًا على وصول كامل إلى أدوات Pro لمدة 7 أيام، دون الحاجة إلى إدخال وسيلة دفع.")
    with st.form("signup_form"):
        full_name = st.text_input("الاسم الكامل", max_chars=120)
        email = st.text_input("البريد الإلكتروني", placeholder="name@example.com", key="signup_email", max_chars=254)
        password = st.text_input("كلمة المرور", type="password", key="signup_password", max_chars=256)
        confirm = st.text_input("تأكيد كلمة المرور", type="password", max_chars=256)
        accepted = st.checkbox("أوافق على الشروط والأحكام وسياسة الخصوصية.")
        submitted = st.form_submit_button("ابدأ التجربة المجانية", type="primary", width="stretch")
    if submitted:
        if not full_name or not email or not password:
            st.warning("أكمل الاسم والبريد وكلمة المرور.")
            return
        if not accepted:
            st.warning("يجب الموافقة على الشروط والأحكام وسياسة الخصوصية لإنشاء الحساب.")
            return
        if len(password) < 8:
            st.warning("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
            return
        if password != confirm:
            st.warning("كلمتا المرور غير متطابقتين.")
            return
        try:
            payload = sign_up(email, password, full_name)
            result = establish_session(payload)
            st.session_state.guest_mode = False
            if result.get("requires_confirmation"):
                st.success("تم إنشاء الحساب. أكد بريدك الإلكتروني ثم سجّل الدخول لبدء تجربة Pro لمدة 7 أيام.")
            else:
                st.success("تم إنشاء الحساب وبدأت تجربة Pro لمدة 7 أيام.")
                st.rerun()
        except Exception:
            st.error("تعذر إنشاء الحساب حاليًا. تحقق من البيانات أو حاول مرة أخرى بعد قليل.")


def _enter_guest() -> None:
    st.session_state.guest_mode = True
    st.session_state.guest_gate_open = False
    st.session_state.active_page = "guest"
    st.rerun()


def render() -> None:
    st.markdown(
        """
        <div style="text-align:center;padding:28px 10px 18px;">
            <div style="font-size:13px;opacity:.7;letter-spacing:1px;">AI BREAKOUT SCANNER</div>
            <div style="font-size:38px;font-weight:800;margin-top:4px;">ابدأ من هنا</div>
            <div style="font-size:16px;opacity:.75;margin-top:8px;">جرّب المنصة كضيف أو أنشئ حسابًا واحصل على Pro لمدة 7 أيام.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 2.4, 1])
    with center:
        if st.button("👀 الدخول كضيف — Guest Preview", width="stretch", key="enter_guest_preview"):
            _enter_guest()
        st.caption("الضيف يرى عينة محدودة جدًا ولا يحصل على حساب أو صلاحيات قاعدة بيانات.")
        st.divider()
        tab_login, tab_signup = st.tabs(["تسجيل الدخول", "إنشاء حساب"])
        with tab_login:
            _login_form()
        with tab_signup:
            _signup_form()
        st.caption("الفترة التجريبية تُمنح مرة واحدة للحساب الجديد، وبعد انتهائها يعود الحساب تلقائيًا إلى Free ما لم يتم تفعيل Pro.")
