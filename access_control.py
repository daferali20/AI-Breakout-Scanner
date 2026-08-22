"""Centralized authentication and plan authorization guards."""
from __future__ import annotations

import streamlit as st

from supabase_auth import has_pro_access, refresh_profile, trial_status


def require_access(required_plan: str = "free") -> dict:
    """Require authentication and optionally Pro or active-trial access."""
    user = st.session_state.get("auth_user") or {}
    token = st.session_state.get("auth_access_token")
    if not user or not token:
        st.error("🔐 يجب تسجيل الدخول للوصول إلى هذه الصفحة.")
        st.page_link("app.py", label="العودة إلى تسجيل الدخول", icon="🔐", width="stretch")
        st.stop()

    try:
        profile = refresh_profile()
    except Exception as exc:
        st.error(f"تعذر التحقق من صلاحية الحساب: {exc}")
        st.stop()

    if required_plan.lower() == "pro" and not has_pro_access(profile):
        trial = trial_status(profile)
        if trial.get("ends_at"):
            st.warning("🔒 انتهت الفترة التجريبية. هذه الصفحة متاحة لمشتركي Pro.")
        else:
            st.warning("🔒 هذه الصفحة متاحة لمشتركي Pro فقط.")
        st.info("يمكنك متابعة الأدوات المجانية أو الاشتراك في Pro لاستعادة جميع الميزات.")
        st.page_link("app.py", label="العودة إلى التطبيق", icon="🏠", width="stretch")
        st.stop()

    return profile
