"""Limited public guest preview. No Supabase user session is created here."""
from __future__ import annotations

from datetime import datetime, timezone
import html
import pandas as pd
import streamlit as st

from backend.results_store import get_scan


def _leave_guest() -> None:
    st.session_state.guest_mode = False
    st.session_state.guest_gate_open = False
    st.session_state.active_page = "auth"
    st.rerun()


def _open_gate(symbol: str = "") -> None:
    st.session_state.guest_gate_open = True
    st.session_state.guest_locked_symbol = symbol
    st.rerun()


def _safe(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _change(row) -> float:
    for key in ("change_pct", "percent_change", "change"):
        if key in row and pd.notna(row.get(key)):
            return _safe(row.get(key))
    return 0.0


def _guest_css() -> None:
    st.markdown("""
    <style>
    .guest-hero{padding:28px 30px;border:1px solid #20344c;border-radius:18px;background:linear-gradient(135deg,#0c1726 0%,#0a1320 55%,#15152d 100%);margin:8px 0 18px}
    .guest-kicker{font-size:12px;font-weight:800;letter-spacing:1.6px;color:#7e8cff;margin-bottom:10px}
    .guest-title{font-size:34px;font-weight:850;line-height:1.2;color:#f5f8ff}
    .guest-sub{font-size:16px;color:#9cabc0;margin-top:10px;max-width:780px;line-height:1.8}
    .guest-live{display:inline-flex;align-items:center;gap:7px;margin-top:16px;padding:7px 11px;border:1px solid #24405a;border-radius:999px;color:#68e0ad;font-size:12px;font-weight:750;background:#0b1b24}
    .guest-dot{width:7px;height:7px;border-radius:50%;background:#38d996;box-shadow:0 0 10px #38d996}
    .guest-section{font-size:22px;font-weight:800;margin:28px 0 4px}
    .guest-section-sub{color:#7f91a9;font-size:13px;margin-bottom:15px}
    .guest-lock-card{border:1px solid #21354d;border-radius:14px;padding:17px;background:#0c1725;min-height:105px}
    .guest-lock-card b{display:block;font-size:15px;margin-bottom:7px;color:#edf3ff}.guest-lock-card span{color:#8395ad;font-size:12px;line-height:1.6}
    .guest-score{display:inline-block;padding:6px 10px;border:1px solid #765cff;border-radius:999px;color:#fff;font-weight:800;background:#17163a}
    .guest-hidden{filter:blur(5px);user-select:none;opacity:.55}
    .guest-footer-note{text-align:center;color:#6f8198;font-size:12px;padding:12px 0 4px}
    @media(max-width:700px){.guest-hero{padding:22px 18px}.guest-title{font-size:27px}.guest-sub{font-size:14px}}
    </style>
    """, unsafe_allow_html=True)


def render() -> None:
    _guest_css()
    if not st.session_state.get("guest_started_at"):
        st.session_state.guest_started_at = datetime.now(timezone.utc).isoformat()

    top_left, top_right = st.columns([4.7, 1.3], vertical_alignment="center")
    with top_left:
        st.markdown("""
        <div class="guest-hero">
          <div class="guest-kicker">AI BREAKOUT SCANNER · GUEST PREVIEW</div>
          <div class="guest-title">👀 استكشف فرص السوق قبل إنشاء حسابك</div>
          <div class="guest-sub">شاهد عينة مباشرة من الفرص التي يلتقطها محرك الذكاء الاصطناعي. التسجيل يفتح المسح الكامل، تحليل السهم، السيولة، الزخم، المخاطر والتنبيهات.</div>
          <div class="guest-live"><span class="guest-dot"></span> Preview Mode · بيانات محدودة للعرض</div>
        </div>
        """, unsafe_allow_html=True)
    with top_right:
        if st.button("🔐 تسجيل الدخول", type="primary", width="stretch", key="guest_login_top"):
            st.session_state.auth_default_tab = "login"
            _leave_guest()
        if st.button("🎁 تجربة Pro مجانًا", width="stretch", key="guest_trial_top"):
            st.session_state.auth_default_tab = "signup"
            _leave_guest()

    snapshot = get_scan()
    data = snapshot.get("scan_results", pd.DataFrame())
    last_scan = snapshot.get("last_scan_time") or "آخر مسح محفوظ"
    market_regime = snapshot.get("market_regime")
    regime = market_regime.get("regime", "AI Market") if isinstance(market_regime, dict) else "AI Market"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("حالة المحرك", "🟢 جاهز")
    m2.metric("Market Sample", str(regime))
    m3.metric("Guest Results", "3 فقط")
    m4.metric("Full Access", "🔒 تسجيل")
    st.caption(f"آخر تحديث للفرص: {last_scan}")

    st.markdown('<div class="guest-section">🔥 عينة مباشرة من أفضل الفرص</div><div class="guest-section-sub">نعرض للضيف أهم البيانات الأساسية فقط. بقية التحليل تبقى محمية حتى التسجيل.</div>', unsafe_allow_html=True)

    if not isinstance(data, pd.DataFrame) or data.empty:
        st.info("ستظهر هنا أفضل 3 فرص تلقائيًا عند توفر نتائج آخر مسح. يمكنك استكشاف مزايا المنصة أدناه.")
    else:
        preview = data.head(3).copy()
        for idx, (_, row) in enumerate(preview.iterrows(), 1):
            raw_symbol = str(row.get("symbol", "—")).upper().strip()
            symbol = html.escape(raw_symbol)
            price = _safe(row.get("price"))
            score = _safe(row.get("opportunity_score", row.get("setup_score", 0)))
            change = _change(row)
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([1.25, 1.15, 1.15, 1.2, 1.35], vertical_alignment="center")
                c1.markdown(f"### {symbol}")
                c1.caption(f"AI Opportunity #{idx}")
                c2.metric("السعر", f"${price:,.2f}" if price else "—")
                c3.metric("التغير", f"{change:+.2f}%" if change else "—")
                c4.markdown(f"<div style='font-size:12px;color:#8294ad;margin-bottom:7px'>Opportunity Score</div><span class='guest-score'>{score:.1f}/100</span>", unsafe_allow_html=True)
                if c5.button("🔒 استعراض السهم", key=f"guest_view_{raw_symbol}_{idx}", width="stretch"):
                    _open_gate(raw_symbol)

            # A teaser row deliberately reveals the categories, not their values.
            t1, t2, t3, t4 = st.columns(4)
            t1.markdown("**Breakout**  🔒")
            t2.markdown("**Liquidity**  🔒")
            t3.markdown("**Momentum**  🔒")
            t4.markdown("**Risk**  🔒")

    st.markdown('<div class="guest-section">🧠 ماذا يفتح التسجيل؟</div><div class="guest-section-sub">حساب جديد يبدأ بتجربة Pro لمدة 7 أيام دون الحاجة إلى تشغيل أدوات الضيف على بيانات خاصة.</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1: st.markdown('<div class="guest-lock-card"><b>🔎 Market Scanner</b><span>مسح السوق واكتشاف المرشحين بدل الاكتفاء بعينة محدودة.</span></div>', unsafe_allow_html=True)
    with f2: st.markdown('<div class="guest-lock-card"><b>📊 Stock Analysis</b><span>فتح صفحة السهم وقراءة مستويات الفرصة والمخاطر والتأكيد.</span></div>', unsafe_allow_html=True)
    with f3: st.markdown('<div class="guest-lock-card"><b>💧 Liquidity & Momentum</b><span>رؤية قوة السيولة والزخم والحجم النسبي والإشارات المتقدمة.</span></div>', unsafe_allow_html=True)
    with f4: st.markdown('<div class="guest-lock-card"><b>🔔 Alerts & Watchlist</b><span>متابعة الفرص والتنبيهات والأدوات المخصصة للمستخدم.</span></div>', unsafe_allow_html=True)

    st.markdown("### جاهز لرؤية التحليل الكامل؟")
    cta1, cta2, _ = st.columns([1.5, 1.15, 2.35])
    if cta1.button("🎁 ابدأ تجربة Pro لمدة 7 أيام", type="primary", width="stretch", key="guest_signup_main"):
        st.session_state.auth_default_tab = "signup"
        _leave_guest()
    if cta2.button("🔐 لدي حساب بالفعل", width="stretch", key="guest_login_main"):
        st.session_state.auth_default_tab = "login"
        _leave_guest()

    if st.session_state.get("guest_gate_open"):
        locked = st.session_state.get("guest_locked_symbol", "")
        title = f"تحليل {locked}" if locked else "هذه الميزة"
        st.warning(f"🔒 {title} متاح للمستخدمين المسجلين. أنشئ حسابًا لتحصل على تجربة Pro لمدة 7 أيام وتفتح التحليل الكامل.")
        x1, x2 = st.columns(2)
        if x1.button("🎁 إنشاء حساب وفتح التحليل", type="primary", width="stretch", key="guest_signup_gate"):
            st.session_state.auth_default_tab = "signup"
            _leave_guest()
        if x2.button("🔐 تسجيل الدخول", width="stretch", key="guest_signin_gate"):
            st.session_state.auth_default_tab = "login"
            _leave_guest()

    st.divider()
    st.markdown('<div class="guest-footer-note">Guest Preview لا ينشئ حسابًا ولا يمنح صلاحيات إلى قاعدة البيانات. البيانات المتقدمة وتشغيل أدوات المنصة يتطلبان تسجيل الدخول.</div>', unsafe_allow_html=True)
