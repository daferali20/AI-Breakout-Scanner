"""Supabase Auth + profiles integration using REST APIs only."""
from __future__ import annotations
from typing import Any
import requests
import streamlit as st


def _config() -> tuple[str, str]:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL أو SUPABASE_KEY غير موجود في Streamlit Secrets")
    return url, key


def _headers(token: str | None = None) -> dict[str, str]:
    _, key = _config()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        return str(payload.get("msg") or payload.get("message") or payload.get("error_description") or payload.get("error") or response.text)
    except Exception:
        return response.text or f"HTTP {response.status_code}"


def sign_up(email: str, password: str, full_name: str) -> dict[str, Any]:
    url, _ = _config()
    response = requests.post(f"{url}/auth/v1/signup", headers=_headers(), json={"email": email.strip().lower(), "password": password, "data": {"full_name": full_name.strip()}}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    return response.json()


def sign_in(email: str, password: str) -> dict[str, Any]:
    url, _ = _config()
    response = requests.post(f"{url}/auth/v1/token?grant_type=password", headers=_headers(), json={"email": email.strip().lower(), "password": password}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    return response.json()


def request_password_reset(email: str) -> None:
    url, _ = _config()
    redirect_to = str(st.secrets.get("PASSWORD_RESET_REDIRECT_URL", "")).strip()
    params = {"redirect_to": redirect_to} if redirect_to else None
    response = requests.post(
        f"{url}/auth/v1/recover",
        headers=_headers(),
        params=params,
        json={"email": email.strip().lower()},
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError(_error_message(response))


def fetch_profile(user_id: str, access_token: str) -> dict[str, Any]:
    url, _ = _config()
    response = requests.get(f"{url}/rest/v1/profiles", headers={**_headers(access_token), "Accept": "application/json"}, params={"id": f"eq.{user_id}", "select": "id,email,full_name,role,subscription_status,created_at,updated_at", "limit": "1"}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    rows = response.json()
    return rows[0] if rows else {}


def refresh_profile() -> dict[str, Any]:
    user = st.session_state.get("auth_user") or {}
    token = st.session_state.get("auth_access_token")
    user_id = str(user.get("id", "")).strip()
    if not user_id or not token:
        raise RuntimeError("جلسة المستخدم غير متاحة.")
    profile = fetch_profile(user_id, str(token))
    st.session_state.user_profile = profile
    status = str(profile.get("subscription_status", "free") or "free").lower()
    st.session_state.plan_selected = "pro" if status == "pro" else "free"
    return profile


def update_profile_name(full_name: str) -> dict[str, Any]:
    user = st.session_state.get("auth_user") or {}
    token = st.session_state.get("auth_access_token")
    user_id = str(user.get("id", "")).strip()
    if not user_id or not token:
        raise RuntimeError("جلسة المستخدم غير متاحة.")
    url, _ = _config()
    response = requests.patch(f"{url}/rest/v1/profiles", headers={**_headers(str(token)), "Prefer": "return=representation"}, params={"id": f"eq.{user_id}"}, json={"full_name": full_name.strip()}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    rows = response.json()
    profile = rows[0] if rows else fetch_profile(user_id, str(token))
    st.session_state.user_profile = profile
    return profile


def _admin_headers() -> dict[str, str]:
    _config()
    service_key = str(st.secrets.get("SUPABASE_SECRET_KEY", "") or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
    if not service_key:
        raise RuntimeError("SUPABASE_SECRET_KEY غير موجود في Streamlit Secrets")
    return {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Content-Type": "application/json", "Accept": "application/json"}


def _require_admin() -> None:
    profile = refresh_profile()
    if str(profile.get("role", "user")).lower() != "admin":
        raise PermissionError("Admin access required")


def admin_list_profiles() -> list[dict[str, Any]]:
    _require_admin()
    url, _ = _config()
    response = requests.get(f"{url}/rest/v1/profiles", headers=_admin_headers(), params={"select": "id,email,full_name,role,subscription_status,created_at,updated_at", "order": "created_at.desc"}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    return response.json()


def admin_update_user(user_id: str, subscription_status: str, role: str) -> dict[str, Any]:
    _require_admin()
    if subscription_status not in {"free", "pro"}:
        raise ValueError("خطة غير صالحة")
    if role not in {"user", "admin"}:
        raise ValueError("دور غير صالح")
    current_id = str((st.session_state.get("auth_user") or {}).get("id", ""))
    if user_id == current_id and role != "admin":
        raise ValueError("لا يمكنك إزالة صلاحية Admin من حسابك الحالي من داخل اللوحة.")
    url, _ = _config()
    response = requests.patch(f"{url}/rest/v1/profiles", headers={**_admin_headers(), "Prefer": "return=representation"}, params={"id": f"eq.{user_id}"}, json={"subscription_status": subscription_status, "role": role}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))
    rows = response.json()
    return rows[0] if rows else {}


def establish_session(auth_payload: dict[str, Any]) -> dict[str, Any]:
    user = auth_payload.get("user") or {}
    access_token = auth_payload.get("access_token")
    if not user:
        raise RuntimeError("لم يرجع Supabase بيانات المستخدم.")
    if not access_token:
        return {"user": user, "profile": {}, "requires_confirmation": True}
    profile = fetch_profile(str(user.get("id", "")), str(access_token))
    st.session_state.auth_user = user
    st.session_state.auth_access_token = access_token
    st.session_state.auth_refresh_token = auth_payload.get("refresh_token")
    st.session_state.user_profile = profile
    status = str(profile.get("subscription_status", "free") or "free").lower()
    st.session_state.plan_selected = "pro" if status == "pro" else "free"
    st.session_state.active_page = "dashboard" if status == "pro" else "free_home"
    return {"user": user, "profile": profile, "requires_confirmation": False}


def logout() -> None:
    token = st.session_state.get("auth_access_token")
    if token:
        try:
            url, _ = _config()
            requests.post(f"{url}/auth/v1/logout", headers=_headers(token), timeout=10)
        except Exception:
            pass
    for key in ("auth_user", "auth_access_token", "auth_refresh_token", "user_profile", "plan_selected"):
        st.session_state.pop(key, None)
    st.session_state.active_page = "auth"
