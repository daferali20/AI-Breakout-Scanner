"""صفحة حساب المستخدم والخطة الحالية."""
from __future__ import annotations

import streamlit as st

from supabase_auth import has_pro_access, refresh_profile, trial_status, update_profile_name

BUILD_TAG = "trial-debug-2026-08-22-0040"


def render() -> None:
    try:
        profile = refresh_profile()
    except Exception:
        profile = st.session_state.get("user_profile") or {}
    user = st.session_state.get("auth_user") or {}

    st.title("👤 حسابي")
    st.caption("إدارة بيانات الحساب ومراجعة الخطة والفترة التجريبية.")
    st.caption(f"Build: {BUILD_TAG}")

    name = str(profile.get("full_name") or user.get("email") or "مستخدم")
    email = str(profile.get("email") or user.get("email") or "غير متاح")
    role = str(profile.get("role") or "user")
    status = str(profile.get("subscription_status") or "free").lower()
    trial = trial_status(profile)
    pro_access = has_pro_access(profile)

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
            if status == "pro":
                st.metric("الخطة", "👑 Pro")
                st.success("الخطة المدفوعة مفعّلة.")
            elif trial.get("active"):
                st.metric("الخطة", "🎁 تجربة Pro")
                st.success(f"الفترة التجريبية مفعلة — متبقي تقريبًا {trial['days_left']} يوم.")
                if profile.get("trial_ends_at"):
                    st.caption(f"تنتهي التجربة: {profile['trial_ends_at']}")
            else:
                st.metric("الخطة", "🟢 Free")
                if profile.get("trial_ends_at"):
                    st.warning("انتهت الفترة التجريبية. يمكنك الاستمرار بالخطة المجانية أو الاشتراك في Pro.")
                else:
                    st.info("أنت تستخدم الخطة المجانية حاليًا.")

    if trial.get("active") and status != "pro":
        st.info("🎁 خلال التجربة لديك وصول كامل إلى صفحات وأدوات Pro. بعد انتهاء المدة يعود الحساب تلقائيًا إلى صلاحيات Free ما لم يتم تفعيل اشتراك Pro.")

    with st.expander("🧪 تشخيص الفترة التجريبية", expanded=True):
        d1, d2, d3 = st.columns(3)
        d1.metric("trial_active", str(bool(trial.get("active"))))
        d2.metric("days_left", int(trial.get("days_left", 0) or 0))
        d3.metric("pro_access", str(bool(pro_access)))
        st.write("trial_started_at:", profile.get("trial_started_at"))
        st.write("trial_ends_at:", profile.get("trial_ends_at"))

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
    if a.button("🔄 تحديث الحساب", width="stretch"):
        try:
            refresh_profile()
            st.success("تم تحديث بيانات الحساب والخطة.")
            st.rerun()
        except Exception as exc:
            st.error(f"تعذر تحديث الحساب: {exc}")

    if b.button("🏠 العودة للرئيسية", width="stretch"):
        st.session_state.active_page = "dashboard" if pro_access else "free_home"
        st.rerun()

    st.divider()
    st.subheader("🔐 الأمان")
    st.write("تتم إدارة المصادقة وكلمة المرور عبر نظام المصادقة الآمن.")
    st.caption("التطبيق لا يعرض كلمة المرور ولا يخزنها داخل Streamlit.")
