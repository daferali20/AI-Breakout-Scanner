"""لوحة إدارة المستخدمين والاشتراكات."""
from __future__ import annotations
from datetime import datetime
import streamlit as st
from supabase_auth import admin_list_profiles, admin_update_user, refresh_profile, trial_status


def _fmt_date(value) -> str:
    if not value:
        return "غير متاح"
    text = str(value)
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return text[:16]


def _display_plan(row: dict) -> str:
    if str(row.get("subscription_status", "free") or "free").lower() == "pro":
        return "Pro"
    return "Trial" if trial_status(row).get("active") else "Free"


def render() -> None:
    profile = refresh_profile()
    if str(profile.get("role", "user")).lower() != "admin":
        st.error("⛔ لا تملك صلاحية الوصول إلى لوحة الإدارة.")
        st.stop()

    top1, top2 = st.columns([4, 1])
    with top1:
        st.title("🛡️ لوحة الإدارة")
        st.caption("إدارة المستخدمين والخطط والصلاحيات والفترات التجريبية.")
    with top2:
        if st.button("🔄 تحديث البيانات", width="stretch"):
            st.rerun()

    try:
        users = admin_list_profiles()
    except Exception as exc:
        st.error(f"تعذر تحميل المستخدمين: {exc}")
        st.info("تأكد من وجود SUPABASE_SECRET_KEY الصحيح وصلاحيات الخدمة على public.profiles.")
        return

    total = len(users)
    trial_count = sum(bool(trial_status(x).get("active")) and str(x.get("subscription_status", "free")).lower() != "pro" for x in users)
    pro_count = sum(str(x.get("subscription_status", "free")).lower() == "pro" for x in users)
    free_count = sum(_display_plan(x) == "Free" for x in users)
    admin_count = sum(str(x.get("role", "user")).lower() == "admin" for x in users)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 المستخدمون", total)
    c2.metric("🎁 Trial", trial_count)
    c3.metric("🟢 Free", free_count)
    c4.metric("👑 Pro", pro_count)
    c5.metric("🛡️ Admin", admin_count)

    st.divider()
    f1, f2, f3 = st.columns([2.2, 1, 1])
    query = f1.text_input("🔎 البحث", placeholder="الاسم أو البريد الإلكتروني")
    plan_filter = f2.selectbox("الخطة", ["الكل", "trial", "free", "pro"])
    role_filter = f3.selectbox("الدور", ["الكل", "user", "admin"])

    filtered = users
    if query.strip():
        q = query.strip().lower()
        filtered = [x for x in filtered if q in str(x.get("email", "")).lower() or q in str(x.get("full_name", "")).lower()]
    if plan_filter != "الكل":
        filtered = [x for x in filtered if _display_plan(x).lower() == plan_filter]
    if role_filter != "الكل":
        filtered = [x for x in filtered if str(x.get("role", "user")).lower() == role_filter]

    st.caption(f"عرض {len(filtered)} من أصل {total} مستخدم")

    for row in filtered:
        uid = str(row.get("id", ""))
        email = str(row.get("email", "—"))
        name = str(row.get("full_name") or "بدون اسم")
        current_plan = str(row.get("subscription_status", "free") or "free").lower()
        current_role = str(row.get("role", "user") or "user").lower()
        created_at = _fmt_date(row.get("created_at"))
        updated_at = _fmt_date(row.get("updated_at"))
        trial = trial_status(row)
        display_plan = _display_plan(row)

        with st.container(border=True):
            a, b, c, d = st.columns([2.2, 2.5, 1, 1])
            a.markdown(f"### {name}")
            a.caption(email)
            b.caption(f"ID: {uid}")
            b.caption(f"انضم: {created_at}")
            b.caption(f"آخر تحديث: {updated_at}")
            if trial.get("active") and current_plan != "pro":
                b.caption(f"🎁 متبقي من التجربة: ~{trial['days_left']} يوم")
            c.metric("الخطة", display_plan)
            d.metric("الدور", "Admin" if current_role == "admin" else "User")

            e1, e2, e3 = st.columns([1.4, 1.4, 1])
            new_plan = e1.selectbox("تغيير الخطة", ["free", "pro"], index=1 if current_plan == "pro" else 0, key=f"plan_{uid}")
            new_role = e2.selectbox("تغيير الدور", ["user", "admin"], index=1 if current_role == "admin" else 0, key=f"role_{uid}")
            changed = new_plan != current_plan or new_role != current_role
            if e3.button("💾 حفظ", key=f"save_{uid}", width="stretch", disabled=not changed):
                try:
                    admin_update_user(uid, subscription_status=new_plan, role=new_role)
                    st.success(f"تم تحديث {email}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"تعذر التحديث: {exc}")

    if not filtered:
        st.info("لا توجد نتائج تطابق الفلاتر الحالية.")
