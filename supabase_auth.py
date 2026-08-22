"""Supabase Auth + profiles integration using REST APIs only."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import requests
import streamlit as st


def _config() -> tuple[str, str]:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    key = str(st.secrets.get("SUPABASE_PUBLISHABLE_KEY", "") or st.secrets.get("SUPABASE_KEY", "")).strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL أو SUPABASE_PUBLISHABLE_KEY غير موجود في Streamlit Secrets")
    return url, key


def _headers(token: str | None = None) -> dict[str, str]:
    _, key = _config()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _admin_headers() -> dict[str, str]:
    secret_key = str(st.secrets.get("SUPABASE_SECRET_KEY", "") or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
    if not secret_key:
        raise RuntimeError("SUPABASE_SECRET_KEY غير موجود في Streamlit Secrets")
    headers = {"apikey": secret_key, "Content-Type": "application/json", "Accept": "application/json"}
    if secret_key.count(".") == 2:
        headers["Authorization"] = f"Bearer {secret_key}"
    return headers


def _error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        return str(payload.get("msg") or payload.get("message") or payload.get("error_description") or payload.get("error") or response.text)
    except Exception:
        return response.text or f"HTTP {response.status_code}"


def _parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def trial_status(profile: dict[str, Any]) -> dict[str, Any]:
    start = _parse_utc(profile.get("trial_started_at"))
    end = _parse_utc(profile.get("trial_ends_at"))
    now = datetime.now(timezone.utc)
    active = bool(start and end and start <= now < end)
    seconds_left = max(0, int((end - now).total_seconds())) if end else 0
    days_left = (seconds_left + 86399) // 86400 if seconds_left else 0
    return {"active": active, "started_at": start, "ends_at": end, "seconds_left": seconds_left, "days_left": days_left}


def has_pro_access(profile: dict[str, Any]) -> bool:
    status = str(profile.get("subscription_status", "free") or "free").lower()
    return status == "pro" or trial_status(profile)["active"]


def _sync_entitlement_session(profile: dict[str, Any]) -> None:
    trial = trial_status(profile)
    st.session_state.trial_active = bool(trial["active"])
    st.session_state.trial_days_left = int(trial["days_left"])
    st.session_state.trial_ends_at = profile.get("trial_ends_at")
    st.session_state.plan_selected = "pro" if has_pro_access(profile) else "free"


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


def refresh_auth_session(refresh_token: str) -> dict[str, Any]:
    """Exchange a Supabase refresh token for a fresh access/refresh token pair."""
    url, _ = _config()
    response = requests.post(
        f"{url}/auth/v1/token?grant_type=refresh_token",
        headers=_headers(),
        json={"refresh_token": refresh_token},
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError(_error_message(response))
    return response.json()


def request_password_reset(email: str) -> None:
    url, _ = _config()
    redirect_to = str(st.secrets.get("PASSWORD_RESET_REDIRECT_URL", "")).strip()
    params = {"redirect_to": redirect_to} if redirect_to else None
    response = requests.post(f"{url}/auth/v1/recover", headers=_headers(), params=params, json={"email": email.strip().lower()}, timeout=20)
    if not response.ok:
        raise RuntimeError(_error_message(response))


def _fetch_profile_server(user_id: str) -> dict[str, Any]:
    url, _ = _config()
    select = "id,email,full_name,role,subscription_status,trial_started_at,trial_ends_at,created_at,updated_at"
    response = requests.get(f"{url}/rest/v1/profiles", headers=_admin_headers(), params={"id": f"eq.{user_id}", "select": select, "limit": "1"}, timeout=20)
    if not response.ok:
        raise RuntimeError(f"{response.status_code}: {_error_message(response)}")
    rows = response.json()
    return rows[0] if rows else {}


def fetch_profile(user_id: str, access_token: str) -> dict[str, Any]:
    url, _ = _config()
    headers = {**_headers(access_token), "Accept": "application/json"}
    select = "id,email,full_name,role,subscription_status,trial_started_at,trial_ends_at,created_at,updated_at"
    response = requests.get(f"{url}/rest/v1/profiles", headers=headers, params={"id": f"eq.{user_id}", "select": select, "limit": "1"}, timeout=20)
    profile: dict[str, Any] = {}
    if response.ok:
        rows = response.json()
        profile = rows[0] if rows else {}
    needs_server_entitlement = not profile or "subscription_status" not in profile or "trial_started_at" not in profile or "trial_ends_at" not in profile
    if needs_server_entitlement:
        return _fetch_profile_server(user_id)
    return profile


def refresh_profile() -> dict[str, Any]:
    user = st.session_state.get("auth_user") or {}
    token = st.session_state.get("auth_access_token")
    user_id = str(user.get("id", "")).strip()
    if not user_id or not token:
        raise RuntimeError("جلسة المستخدم غير متاحة.")
    profile = fetch_profile(user_id, str(token))
    if str(profile.get("subscription_status", "free") or "free").lower() != "pro" and not profile.get("trial_ends_at"):
        try:
            trusted = _fetch_profile_server(user_id)
            if trusted:
                profile = trusted
        except Exception:
            pass
    st.session_state.user_profile = profile
    _sync_entitlement_session(profile)
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
    profile = fetch_profile(user_id, str(token))
    st.session_state.user_profile = profile
    _sync_entitlement_session(profile)
    return profile


def _require_admin() -> None:
    profile = refresh_profile()
    if str(profile.get("role", "user")).lower() != "admin":
        raise PermissionError("Admin access required")


def admin_list_profiles() -> list[dict[str, Any]]:
    _require_admin()
    url, _ = _config()
    select = "id,email,full_name,role,subscription_status,trial_started_at,trial_ends_at,created_at,updated_at"
    response = requests.get(f"{url}/rest/v1/profiles", headers=_admin_headers(), params={"select": select, "order": "created_at.desc"}, timeout=20)
    if not response.ok:
        raise RuntimeError(f"{response.status_code}: {_error_message(response)}")
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
        raise RuntimeError(f"{response.status_code}: {_error_message(response)}")
    rows = response.json()
    return rows[0] if rows else {}


def establish_session(auth_payload: dict[str, Any], remember: bool = False) -> dict[str, Any]:
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
    st.session_state.remember_me = bool(remember)
    _sync_entitlement_session(profile)
    st.session_state.active_page = "dashboard" if has_pro_access(profile) else "free_home"
    if remember and auth_payload.get("refresh_token"):
        try:
            from auth_persistence import save_refresh_token
            save_refresh_token(str(auth_payload.get("refresh_token")))
        except Exception:
            pass
    return {"user": user, "profile": profile, "requires_confirmation": False}


def restore_persistent_session() -> bool:
    """Restore a remembered Supabase session after browser refresh/reconnect."""
    if st.session_state.get("auth_user"):
        return True
    try:
        from auth_persistence import clear_refresh_token, load_refresh_token, save_refresh_token
        refresh_token = load_refresh_token()
    except Exception:
        return False
    if not refresh_token:
        return False
    try:
        payload = refresh_auth_session(refresh_token)
        result = establish_session(payload, remember=True)
        new_refresh = payload.get("refresh_token")
        if new_refresh:
            save_refresh_token(str(new_refresh))
        return not bool(result.get("requires_confirmation"))
    except Exception:
        try:
            clear_refresh_token()
        except Exception:
            pass
        return False


def logout() -> None:
    token = st.session_state.get("auth_access_token")
    if token:
        try:
            url, _ = _config()
            requests.post(f"{url}/auth/v1/logout", headers=_headers(token), timeout=10)
        except Exception:
            pass
    try:
        from auth_persistence import clear_refresh_token
        clear_refresh_token()
    except Exception:
        pass
    for key in ("auth_user", "auth_access_token", "auth_refresh_token", "user_profile", "plan_selected", "trial_active", "trial_days_left", "trial_ends_at", "remember_me"):
        st.session_state.pop(key, None)
    st.session_state.active_page = "auth"
