"""Limited public guest preview. No Supabase user session is created here."""
from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd
import streamlit as st

from backend.results_store import get_scan


def _leave_guest() -> None:
    st.session_state.guest_mode = False
    st.session_state.guest_gate_open = False
    st.session_state.active_page = "auth"
    st.rerun()


def _open_gate() -> None:
    st.session_state.guest_gate_open = True
    st.rerun()


def _safe(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def render() -> None:
    started = st.session_state.get("guest_started_at")
    if not started:
        st.session_state.guest_started_at = datetime.now(timezone.utc).isoformat()

    top_left, top_right = st.columns([4.5, 1.5])
    with top_left:
        st.markdown("# 👀 Guest Preview")
        st.caption("استكشف لمحة محدودة من AI Breakout Scanner قبل إنشاء الحساب.")
    with top_right:
        if st.button("🔐 تسجيل الدخول / إنشاء حساب", type="primary", width="stretch", key="guest_login_top"):
            _leave_guest()

    st.info("وضع الضيف يعرض بيانات محدودة فقط. التحليل الكامل، تشغيل Scanner، السيولة، الزخم، المخاطر والتنبيهات تتطلب حسابًا.")

    snapshot = get_scan()
    data = snapshot.get("scan_results", pd.DataFrame())
    if not isinstance(data, pd.DataFrame) or data.empty:
        st.markdown("### لمحة عن المنصة")
        c1, c2, c3 = st.columns(3)
        c1.metric("AI Ranking", "متاح")
        c2.metric("Market Scanner", "🔒")
        c3.metric("Stock Analysis", "🔒")
        st.caption("ستظهر هنا عينة من فرص السوق عند توفر آخر نتائج المسح.")
    else:
        preview = data.head(3).copy()
        st.markdown("### 🔥 عينة من الفرص")
        st.caption("يتم عرض 3 فرص فقط للضيف، مع إخفاء بيانات التحليل المتقدمة.")

        for idx, (_, row) in enumerate(preview.iterrows(), 1):
            symbol = str(row.get("symbol", "—")).upper().strip()
            price = _safe(row.get("price"))
            score = _safe(row.get("opportunity_score", row.get("setup_score", 0)))
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([1.35, 1.2, 1.3, 1.15], vertical_alignment="center")
                c1.markdown(f"### {symbol}")
                c1.caption(f"Opportunity #{idx}")
                c2.metric("Price", f"${price:,.2f}" if price else "—")
                c3.metric("AI Opportunity", f"{score:.1f}/100")
                if c4.button("🔒 عرض التحليل", key=f"guest_view_{symbol}_{idx}", width="stretch"):
                    _open_gate()

        st.markdown("### ما الذي ستحصل عليه بعد التسجيل؟")
        a, b, c, d = st.columns(4)
        a.metric("Breakout", "🔒 Full")
        b.metric("Liquidity", "🔒 Full")
        c.metric("Momentum", "🔒 Full")
        d.metric("Risk", "🔒 Full")

    if st.session_state.get("guest_gate_open"):
        st.warning("🔒 هذه الميزة متاحة للمستخدمين المسجلين. أنشئ حسابًا مجانًا لتحصل على تجربة Pro لمدة 7 أيام.")
        x1, x2 = st.columns(2)
        if x1.button("🎁 إنشاء حساب وبدء تجربة 7 أيام", type="primary", width="stretch", key="guest_signup_cta"):
            st.session_state.auth_default_tab = "signup"
            _leave_guest()
        if x2.button("🔐 لدي حساب بالفعل", width="stretch", key="guest_signin_cta"):
            st.session_state.auth_default_tab = "login"
            _leave_guest()

    st.divider()
    st.caption("Guest Preview لا ينشئ حسابًا ولا يمنح صلاحيات وصول إلى قاعدة البيانات. التسجيل مطلوب لاستخدام أدوات المنصة.")
