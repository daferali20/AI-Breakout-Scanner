"""لوحة إدارة المستخدمين والاشتراكات."""
from __future__ import annotations

import streamlit as st
from supabase_auth import admin_list_profiles, admin_update_user, refresh_profile


def render() -> None:
    profile = refresh_profile()
    if str(profile.get("role", "user")).lower() != "admin":
        st.error("⛔ لا تملك صلاحية الوصول إلى لوحة الإدارة.")
        st.stop()

    st.title("🛡️ لوحة الإدارة")
    st.caption("إدارة المستخدمين والخطط من Supabase.")

    try:
        users = admin_list_profiles()
    except Exception as exc:
        st.error(f"تعذر تحميل المستخدمين: {exc}")
        st.info("أضف SUPABASE_SERVICE_ROLE_KEY إلى Streamlit Secrets لتفعيل وظائف الإدارة. لا تستخدم هذا المفتاح في الواجهة العامة.")
        return

    total = len(users)
    free_count = sum(str(x.get("subscription_status", "free")).lower() == "free" for x in users)
    pro_count = sum(str(x.get("subscription_status", "free")).lower() == "pro" for x in users)
    admin_count = sum(str(x.get("role", "user")).lower() == "admin" for x in users)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 المستخدمون", total)
    c2.metric("🟢 Free", free_count)
    c3.metric("👑 Pro", pro_count)
    c4.metric("🛡️ Admin", admin_count)

    st.divider()
    query = st.text_input("🔎 البحث", placeholder="الاسم أو البريد الإلكتروني")
    filtered = users
    if query.strip():
        q = query.strip().lower()
        filtered = [x for x in users if q in str(x.get("email", "")).lower() or q in str(x.get("full_name", "")).lower()]

    for row in filtered:
        uid = str(row.get("id", ""))
        email = str(row.get("email", "—"))
        name = str(row.get("full_name") or "بدون اسم")
        current_plan = str(row.get("subscription_status", "free") or "free").lower()
        current_role = str(row.get("role", "user") or "user").lower()
        with st.container(border=True):
            a, b, c, d = st.columns([2, 2.4, 1, 1])
            a.markdown(f"**{name}**")
            a.caption(email)
            b.caption(f"ID: {uid}")
            c.write("👑 Pro" if current_plan == "pro" else "🟢 Free")
            d.write("🛡️ Admin" if current_role == "admin" else "👤 User")

            e1, e2, e3 = st.columns([1.4, 1.4, 1])
            new_plan = e1.selectbox("الخطة", ["free", "pro"], index=1 if current_plan == "pro" else 0, key=f"plan_{uid}")
            new_role = e2.selectbox("الدور", ["user", "admin"], index=1 if current_role == "admin" else 0, key=f"role_{uid}")
            if e3.button("💾 حفظ", key=f"save_{uid}", width="stretch"):
                try:
                    admin_update_user(uid, subscription_status=new_plan, role=new_role)
                    st.success(f"تم تحديث {email}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"تعذر التحديث: {exc}")
