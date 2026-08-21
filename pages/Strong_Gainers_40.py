"""🚀 Independent +40% gainers dashboard."""
from __future__ import annotations
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from access_control import require_access
from backend.gainers_universe import get_universe, universe_status
from backend.strong_gainers import MIN_PRICE, MAX_PRICE, analyze_gainers, discover_strong_gainers

st.set_page_config(page_title="الأسهم الصاعدة +40%", page_icon="🚀", layout="wide")
require_access("free")
st.title("🚀 Strong Gainers 40")
st.caption("قائمة المتصدرين الحقيقيين للسوق: نكتشف أعلى الأسهم ارتفاعًا أولًا، ثم نحلل الزخم والسيولة والتداول النسبي.")

status = universe_status()
u1, u2, u3 = st.columns(3)
u1.metric("🇺🇸 الكون الأمريكي", f"{status['count']:,} رمز")
u2.metric("⚡ تحديث الاكتشاف", "كل 3 دقائق")
u3.metric("📡 المصادر", "Yahoo Custom + Nasdaq")

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
auto = c1.toggle("🤖 اكتشاف تلقائي", value=True)
manual = c2.text_input("🔎 سهم/رموز إضافية", placeholder="RFAI, USDE, SDOT")
limit = c3.selectbox("حد المرشحين للتحليل", [50, 100, 150, 250], index=3, format_func=lambda x: f"{x:,} مرشح")
price_range = c4.selectbox("💵 نطاق السعر", ["$0.40 – $50", "$0.40 – $10", "$1 – $50", "مخصص"], index=0)
if price_range == "$0.40 – $10": min_price, max_price = 0.40, 10.0
elif price_range == "$1 – $50": min_price, max_price = 1.0, 50.0
elif price_range == "مخصص":
    p1, p2 = st.columns(2)
    min_price = p1.number_input("أقل سعر", min_value=0.01, value=0.40, step=0.10)
    max_price = p2.number_input("أعلى سعر", min_value=0.02, value=50.00, step=1.00)
else:
    min_price, max_price = MIN_PRICE, MAX_PRICE

if st.button("🔄 تحديث المتصدرين الآن", type="primary", width="stretch"):
    with st.spinner("جلب أعلى الأسهم ارتفاعًا في السوق ثم تحليل السيولة والزخم..."):
        if auto:
            df, stats = discover_strong_gainers(limit=limit, threshold=40.0, min_price=min_price, max_price=max_price)
        else:
            symbols = [x.strip().upper() for x in manual.replace("\n", ",").split(",") if x.strip()]
            df, stats = analyze_gainers(symbols or list(get_universe(limit)), threshold=40.0, min_price=min_price, max_price=max_price)
        st.session_state["strong_gainers_40"] = df
        st.session_state["strong_gainers_40_stats"] = stats

if "strong_gainers_40" not in st.session_state and auto:
    with st.spinner("جلب المتصدرين الحاليين..."):
        df, stats = discover_strong_gainers(limit=limit, threshold=40.0, min_price=min_price, max_price=max_price)
        st.session_state["strong_gainers_40"] = df
        st.session_state["strong_gainers_40_stats"] = stats

df = st.session_state.get("strong_gainers_40")
stats = st.session_state.get("strong_gainers_40_stats", {})
if df is None:
    st.info("اضغط «تحديث المتصدرين الآن» لبدء الفحص.")
    st.stop()

with st.expander("🔎 تشخيص الاكتشاف", expanded=df.empty):
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("مكتشفون +40%", f"{stats.get('prefiltered', 0):,}")
    d2.metric("لتحليل التاريخ", f"{stats.get('requested', 0):,}")
    d3.metric("بيانات صالحة", f"{stats.get('with_data', 0):,}")
    d4.metric("ضمن السعر", f"{stats.get('price_range', 0):,}")
    d5.metric("نتائج نهائية", f"{stats.get('above_threshold', 0):,}")

if df.empty:
    st.warning("لم تصل نتائج +40% صالحة من المصادر الحالية في هذه اللحظة. افتح التشخيص لمعرفة مرحلة التوقف.")
    st.caption(f"نطاق السعر: ${min_price:.2f} – ${max_price:.2f}")
    st.stop()

# This is a market-gainers page: rank by actual percentage move first.
df = df.sort_values(["change_pct", "gainer_score", "liquidity_score"], ascending=False).reset_index(drop=True)

st.subheader("🏆 أعلى الأسهم ارتفاعًا الآن")
top = df.head(15)
for i, (_, row) in enumerate(top.iterrows(), 1):
    with st.container(border=True):
        a, b, c, d, e, f = st.columns([0.65, 1.25, 1, 1, 1, 1.25])
        a.markdown(f"## #{i}")
        b.markdown(f"### {row['symbol']}\n${row['price']:.2f}")
        c.metric("📈 الارتفاع", f"+{row['change_pct']:.2f}%")
        d.metric("⚡ الزخم", f"{row['momentum_score']:.0f}/100")
        e.metric("💧 السيولة", f"{row['liquidity_score']:.0f}/100")
        f.metric("🏆 Score", f"{row['gainer_score']:.1f}")
        st.caption(
            f"{row['strength']} · {row.get('exchange','')} · المصدر: {row.get('source','—')} · "
            f"RVOL {row['relative_volume']:.2f}x · الحجم {int(row['volume']):,} · RSI {row['rsi']:.1f}"
        )

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("🚀 عدد الأسهم +40%", len(df))
c2.metric("🔥 زخم ≥70", int((df["momentum_score"] >= 70).sum()))
c3.metric("💧 سيولة ≥70", int((df["liquidity_score"] >= 70).sum()))
c4.metric("⚡ RVOL ≥2x", int((df["relative_volume"] >= 2).sum()))

st.subheader("📋 جميع المتصدرين")
for _, row in df.head(75).iterrows():
    with st.container(border=True):
        a, b, c, d, e, f = st.columns([1.2, 1, 1, 1, 1, 1.3])
        a.markdown(f"### {row['symbol']}")
        b.metric("الارتفاع", f"+{row['change_pct']:.2f}%")
        c.metric("الزخم", f"{row['momentum_score']:.0f}/100")
        d.metric("السيولة", f"{row['liquidity_score']:.0f}/100")
        e.metric("RVOL", f"{row['relative_volume']:.2f}x")
        f.metric("القوة", row["strength"])
        st.caption(
            f"السعر ${row['price']:.2f} · {row.get('exchange','')} · المصدر {row.get('source','—')} · "
            f"الحجم {int(row['volume']):,} · Dollar Volume ${row['dollar_volume']:,.0f} · RSI {row['rsi']:.1f}"
        )

with st.expander("عرض البيانات الكاملة"):
    columns = [c for c in ["symbol", "price", "change_pct", "volume", "relative_volume", "momentum_score", "liquidity_score", "gainer_score", "exchange", "source"] if c in df.columns]
    st.dataframe(df[columns], width="stretch", hide_index=True)
