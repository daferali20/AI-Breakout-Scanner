"""🚀 Independent +40% gainers dashboard with market and elite lists."""
from __future__ import annotations
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st
from access_control import require_access
from backend.gainers_universe import get_universe, universe_status
from backend.strong_gainers import MIN_PRICE, MAX_PRICE, analyze_gainers, discover_strong_gainers

st.set_page_config(page_title="الأسهم الصاعدة +40%", page_icon="🚀", layout="wide")
require_access("free")


def _technical_catalysts(row) -> list[str]:
    items: list[str] = []
    rvol = float(row.get("relative_volume", 0) or 0)
    momentum = float(row.get("momentum_score", 0) or 0)
    liquidity = float(row.get("liquidity_score", 0) or 0)
    change = float(row.get("change_pct", 0) or 0)
    dollar_volume = float(row.get("dollar_volume", 0) or 0)
    if rvol >= 3:
        items.append("🔥 حجم استثنائي")
    elif rvol >= 2:
        items.append("💧 RVOL مرتفع")
    if liquidity >= 80:
        items.append("💎 سيولة قوية جدًا")
    elif liquidity >= 65:
        items.append("💧 سيولة قوية")
    if momentum >= 80:
        items.append("🚀 زخم قوي جدًا")
    elif momentum >= 70:
        items.append("📈 زخم قوي")
    if dollar_volume >= 20_000_000:
        items.append("💵 تداول نقدي كبير")
    if change >= 100:
        items.append("⚡ تسارع سعري استثنائي")
    elif change >= 60:
        items.append("⚡ تسارع سعري قوي")
    return items


def _build_elite(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    work = df.copy()
    for col in ("change_pct", "momentum_score", "liquidity_score", "relative_volume", "dollar_volume"):
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)
    work["catalysts"] = work.apply(lambda row: _technical_catalysts(row), axis=1)
    work["catalyst_count"] = work["catalysts"].map(len)
    work["elite_score"] = (
        work["momentum_score"] * 0.30
        + work["liquidity_score"] * 0.35
        + work["change_pct"].clip(upper=150) / 150 * 20
        + work["relative_volume"].clip(upper=5) / 5 * 10
        + work["catalyst_count"].clip(upper=5) / 5 * 5
    ).round(1)
    elite = work[
        (work["momentum_score"] >= 65)
        & (work["liquidity_score"] >= 60)
        & ((work["relative_volume"] >= 1.5) | (work["dollar_volume"] >= 5_000_000))
        & (work["catalyst_count"] >= 2)
    ].copy()
    return elite.sort_values(["elite_score", "liquidity_score", "momentum_score", "change_pct"], ascending=False).reset_index(drop=True)


st.title("🚀 الأسهم الأكثر ارتفاعًا +40%")
st.caption("قائمتان: الأولى تعرض المتصدرين الحقيقيين للسوق، والثانية تستخلص نخبة الأسهم الأقوى سيولةً وزخمًا ومحفزًا فنيًا.")

status = universe_status()
u1, u2, u3 = st.columns(3)
u1.metric("🇺🇸 الكون المستقل", f"{status['count']:,} رمز")
u2.metric("💾 تحديث الاكتشاف", "≈ 3 دقائق")
u3.metric("📡 المصادر", "Yahoo Custom + Nasdaq")

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
auto = c1.toggle("🤖 اكتشاف تلقائي", value=True)
manual = c2.text_input("🔎 سهم/رموز إضافية", placeholder="RFAI, USDE, SDOT")
limit = c3.selectbox("حد المرشحين للتحليل", [50, 100, 150, 300, 600], index=2, format_func=lambda x: f"{x:,} مرشح")
price_range = c4.selectbox("💵 نطاق السعر", ["$0.40 – $50", "$0.40 – $10", "$1 – $50", "مخصص"], index=0)
if price_range == "$0.40 – $10":
    min_price, max_price = 0.40, 10.0
elif price_range == "$1 – $50":
    min_price, max_price = 1.0, 50.0
elif price_range == "مخصص":
    p1, p2 = st.columns(2)
    min_price = p1.number_input("أقل سعر", min_value=0.01, value=0.40, step=0.10)
    max_price = p2.number_input("أعلى سعر", min_value=0.02, value=50.00, step=1.00)
else:
    min_price, max_price = MIN_PRICE, MAX_PRICE

if st.button("🔄 تحديث الأسهم +40%", type="primary", width="stretch"):
    with st.spinner("اكتشاف المتصدرين الحقيقيين ثم تحليل السيولة والزخم..."):
        if auto:
            df, stats = discover_strong_gainers(limit=limit, threshold=40.0, min_price=min_price, max_price=max_price)
        else:
            symbols = [x.strip().upper() for x in manual.replace("\n", ",").split(",") if x.strip()]
            df, stats = analyze_gainers(symbols or list(get_universe(limit)), threshold=40.0, min_price=min_price, max_price=max_price)
        st.session_state["strong_gainers_40"] = df
        st.session_state["strong_gainers_40_stats"] = stats
        st.session_state["strong_gainers_40_price_range"] = (min_price, max_price)

if "strong_gainers_40" not in st.session_state and auto:
    with st.spinner("جاري أول اكتشاف تلقائي..."):
        df, stats = discover_strong_gainers(limit=limit, threshold=40.0, min_price=min_price, max_price=max_price)
        st.session_state["strong_gainers_40"] = df
        st.session_state["strong_gainers_40_stats"] = stats
        st.session_state["strong_gainers_40_price_range"] = (min_price, max_price)

df = st.session_state.get("strong_gainers_40")
stats = st.session_state.get("strong_gainers_40_stats", {})
if df is None:
    st.info("اضغط «تحديث الأسهم +40%» لبدء الفحص.")
    st.stop()

with st.expander("🔎 تشخيص عملية المسح", expanded=df.empty):
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("مرشحو +40%", f"{stats.get('prefiltered', 0):,}")
    d2.metric("أرسل للتحليل", f"{stats.get('requested', 0):,}")
    d3.metric("بيانات صالحة", f"{stats.get('with_data', 0):,}")
    d4.metric("ضمن السعر", f"{stats.get('price_range', 0):,}")
    d5.metric("نتائج نهائية", f"{stats.get('above_threshold', 0):,}")

if df.empty:
    st.warning("لم تصل نتائج نهائية حاليًا. جرّب التحديث أثناء جلسة السوق أو الـPremarket.")
    st.stop()

market_df = df.sort_values(["change_pct", "volume"], ascending=False).reset_index(drop=True)
elite_df = _build_elite(market_df)
st.session_state["strong_gainers_40_elite"] = elite_df

m1, m2, m3, m4 = st.columns(4)
m1.metric("🚀 جميع +40%", len(market_df))
m2.metric("🏆 قائمة النخبة", len(elite_df))
m3.metric("💧 سيولة قوية", int((market_df["liquidity_score"] >= 70).sum()))
m4.metric("🔥 زخم قوي", int((market_df["momentum_score"] >= 70).sum()))

list_all, list_elite = st.tabs(["🚀 القائمة 1 — متصدرو السوق", "🏆 القائمة 2 — النخبة الأفضل"])

with list_all:
    st.subheader("🚀 المتصدرون الحقيقيون حسب نسبة الارتفاع")
    st.caption("هذه القائمة لا تنتقي الجودة؛ هدفها إظهار من يتصدر السوق فعليًا ثم ترتيبهم حسب نسبة الارتفاع.")
    for i, (_, row) in enumerate(market_df.head(50).iterrows(), 1):
        with st.container(border=True):
            a, b, c, d, e, f = st.columns([0.55, 1.15, 1, 1, 1, 1.25])
            a.markdown(f"### #{i}")
            b.markdown(f"### {row['symbol']}\n${row['price']:.2f}")
            c.metric("📈 الارتفاع", f"+{row['change_pct']:.1f}%")
            d.metric("💧 السيولة", f"{row['liquidity_score']:.0f}/100")
            e.metric("⚡ الزخم", f"{row['momentum_score']:.0f}/100")
            f.metric("RVOL", f"{row['relative_volume']:.2f}x")
            source = row.get("source", row.get("exchange", ""))
            st.caption(f"{row['strength']} · الحجم: {int(row['volume']):,} · Dollar Volume: ${row['dollar_volume']:,.0f} · المصدر: {source or 'Market discovery'}")

with list_elite:
    st.subheader("🏆 نخبة السيولة والزخم والمحـفز")
    st.caption("يشترط زخمًا وسيولة مناسبين، مع RVOL أو تداول نقدي قوي، ووجود محفزين فنيين على الأقل.")
    if elite_df.empty:
        st.info("لا توجد أسهم تحقق شروط النخبة حاليًا. المتصدر ليس بالضرورة فرصة جيدة؛ ستظهر هنا فقط الأسهم التي تتجمع فيها الجودة والسيولة والزخم.")
    else:
        for i, (_, row) in enumerate(elite_df.head(20).iterrows(), 1):
            catalysts = row.get("catalysts", [])
            with st.container(border=True):
                a, b, c, d, e, f = st.columns([0.55, 1.15, 1, 1, 1, 1.15])
                a.markdown(f"## #{i}")
                b.markdown(f"### {row['symbol']}\n${row['price']:.2f}")
                c.metric("🏆 Elite", f"{row['elite_score']:.1f}")
                d.metric("💧 السيولة", f"{row['liquidity_score']:.0f}/100")
                e.metric("🚀 الزخم", f"{row['momentum_score']:.0f}/100")
                f.metric("📈 الارتفاع", f"+{row['change_pct']:.1f}%")
                st.markdown(" **المحفزات الفنية:** " + " · ".join(catalysts))
                st.caption(f"RVOL: {row['relative_volume']:.2f}x · الحجم: {int(row['volume']):,} · Dollar Volume: ${row['dollar_volume']:,.0f} · RSI: {row['rsi']:.1f}")

with st.expander("📋 عرض البيانات الكاملة"):
    st.markdown("**كل المتصدرين**")
    st.dataframe(market_df, width="stretch", hide_index=True)
    if not elite_df.empty:
        st.markdown("**قائمة النخبة**")
        elite_display = elite_df.copy()
        elite_display["catalysts"] = elite_display["catalysts"].map(lambda x: " | ".join(x))
        st.dataframe(elite_display, width="stretch", hide_index=True)
