"""Centralized authentication and plan authorization guards."""
from __future__ import annotations

import streamlit as st

from supabase_auth import refresh_profile


def require_access(required_plan: str = "free") -> dict:
    """Require an authenticated user and optionally a Pro subscription.

    The subscription is refreshed from Supabase before granting access so a
    client-side/session-state change cannot promote a Free user to Pro.
    """
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

    status = str(profile.get("subscription_status", "free") or "free").lower()
    if required_plan.lower() == "pro" and status != "pro":
        st.warning("🔒 هذه الصفحة متاحة لمشتركي Pro فقط.")
        st.info("يمكنك متابعة الأدوات المجانية من الصفحة الرئيسية لحسابك.")
        st.page_link("app.py", label="العودة إلى التطبيق", icon="🏠", width="stretch")
        st.stop()

    return profile
