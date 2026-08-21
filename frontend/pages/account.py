"""صفحة حساب المستخدم."""
from __future__ import annotations

import streamlit as st


def render() -> None:
    profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}
    plan = st.session_state.get("plan_selected", "free")

    st.title("👤 حسابي")
    st.caption("بيانات الحساب والخطة الحالية.")

    name = str(profile.get("full_name") or user.get("email") or "مستخدم")
    email = str(profile.get("email") or user.get("email") or "غير متاح")
    role = str(profile.get("role") or "user")
    status = str(profile.get("subscription_status") or plan or "free").lower()

    c1, c2 = st.columns([1.3, 1])
    with c1:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(f"**البريد:** {email}")
            st.write(f"**الدور:** {role}")
            st.write(f"**الخطة:** {'👑 Pro' if status == 'pro' else '🟢 Free'}")
            created_at = profile.get("created_at")
            if created_at:
                st.caption(f"تاريخ إنشاء الحساب: {created_at}")

    with c2:
        with st.container(border=True):
            st.markdown("### حالة الاشتراك")
            if status == "pro":
                st.success("👑 الخطة المدفوعة مفعّلة")
                st.write("لديك وصول إلى أدوات Pro المتقدمة.")
            else:
                st.info("🟢 الخطة المجانية")
                st.write("يمكنك استخدام الأدوات الأساسية المتاحة في الخطة المجانية.")
                st.caption("الترقية إلى Pro ستضيف الأدوات المتقدمة عند تفعيل الاشتراكات.")

    st.divider()
    st.subheader("🔐 الأمان")
    st.write("تتم إدارة المصادقة وكلمة المرور عبر Supabase Auth.")
    st.caption("لن يعرض التطبيق كلمة المرور أو يخزنها داخل Streamlit.")
