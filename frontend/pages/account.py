"""صفحة حساب المستخدم والخطة الحالية."""
from __future__ import annotations

import streamlit as st

from supabase_auth import refresh_profile, update_profile_name


def render() -> None:
    profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}
    plan = st.session_state.get("plan_selected", "free")

    st.title("👤 حسابي")
    st.caption("إدارة بيانات الحساب ومراجعة الخطة الحالية.")

    name = str(profile.get("full_name") or user.get("email") or "مستخدم")
    email = str(profile.get("email") or user.get("email") or "غير متاح")
    role = str(profile.get("role") or "user")
    status = str(profile.get("subscription_status") or plan or "free").lower()

    c1, c2 = st.columns([1.4, 1])
    with c1:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(f"**البريد:** {email}")
            st.write(f"**الدور:** {role}")
            created_at = profile.get("created_at")
            if created_at:
                st.caption(f"تاريخ إنشاء الحساب: {created_at}")

    with c2:
        with st.container(border=True):
            st.markdown("### حالة الاشتراك")
            st.metric("الخطة", "👑 Pro" if status == "pro" else "🟢 Free")
            if status == "pro":
                st.success("الخطة المدفوعة مفعّلة.")
            else:
                st.info("أنت تستخدم الخطة المجانية حاليًا.")

    st.divider()
    st.subheader("✏️ تعديل الاسم")
    with st.form("account_name_form"):
        full_name = st.text_input("الاسم الكامل", value=str(profile.get("full_name") or ""))
        submitted = st.form_submit_button("حفظ التعديل", type="primary", width="stretch")
    if submitted:
        if not full_name.strip():
            st.warning("أدخل اسمًا صالحًا.")
        else:
            try:
                update_profile_name(full_name)
                st.success("تم تحديث الاسم بنجاح.")
                st.rerun()
            except Exception as exc:
                st.error(f"تعذر تحديث الاسم: {exc}")

    st.divider()
    a, b = st.columns(2)
    if a.button("🔄 تحديث الحساب من Supabase", width="stretch"):
        try:
            refresh_profile()
            st.success("تم تحديث بيانات الحساب والخطة.")
            st.rerun()
        except Exception as exc:
            st.error(f"تعذر تحديث الحساب: {exc}")

    if b.button("🏠 العودة للرئيسية", width="stretch"):
        st.session_state.active_page = "dashboard" if status == "pro" else "free_home"
        st.rerun()

    st.divider()
    st.subheader("🔐 الأمان")
    st.write("تتم إدارة المصادقة وكلمة المرور عبر Supabase Auth.")
    st.caption("التطبيق لا يعرض كلمة المرور ولا يخزنها داخل Streamlit.")
