"""Encrypted browser persistence for Supabase refresh tokens."""
from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st
from cryptography.fernet import Fernet, InvalidToken

COOKIE_NAME = "ai_breakout_remember"
COOKIE_DAYS = 30


def _fernet() -> Fernet:
    secret = str(
        st.secrets.get("AUTH_COOKIE_SECRET", "")
        or st.secrets.get("SUPABASE_SECRET_KEY", "")
        or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")
    ).strip()
    if not secret:
        raise RuntimeError("AUTH_COOKIE_SECRET أو SUPABASE_SECRET_KEY مطلوب لتشفير جلسة تسجيل الدخول.")
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _manager():
    return stx.CookieManager(key="auth_cookie_manager")


def save_refresh_token(refresh_token: str, remember: bool = False) -> None:
    """Save an encrypted refresh token.

    remember=False -> browser-session cookie (survives page refresh, not browser close).
    remember=True  -> persistent cookie for COOKIE_DAYS days.
    """
    if not refresh_token:
        return
    encrypted = _fernet().encrypt(refresh_token.encode("utf-8")).decode("utf-8")
    kwargs = {
        "key": "set_auth_cookie",
    }
    if remember:
        kwargs["expires_at"] = datetime.now() + timedelta(days=COOKIE_DAYS)
    _manager().set(COOKIE_NAME, encrypted, **kwargs)


def load_refresh_token() -> str | None:
    try:
        encrypted = _manager().get(COOKIE_NAME)
    except Exception:
        return None
    if not encrypted:
        return None
    try:
        return _fernet().decrypt(str(encrypted).encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        clear_refresh_token()
        return None


def clear_refresh_token() -> None:
    try:
        _manager().delete(COOKIE_NAME, key="delete_auth_cookie")
    except Exception:
        pass
