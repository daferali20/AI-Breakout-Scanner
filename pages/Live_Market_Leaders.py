"""📡 Separate live market leaders page using non-Yahoo discovery."""
from __future__ import annotations
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st
from backend.live_market_leaders import discover_live_leaders
from backend.strong_gainers import analyze_gainers

st.set_page_config(page_title="Live Market Leaders", page_icon="📡", layout="wide")

# Local auth guard avoids the import issue seen with root-level access_control.py.
if not st.session_state.get("auth_user"):
    st.error("🔒 يجب تسجيل الدخول أولًا.")
    st.stop()


def _build_elite(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    work = df.copy()
    for col in ("change_pct", "momentum_score", "liquidity_score", "relative_volume", "dollar_volume"):
        work[col] = pd.to_numeric(work.get(col, 0), errors="coerce").fillna(0)
    work["elite_score"] = (
        work["momentum_score"] * 0.34
        + work["liquidity_score"] * 0.36
        + work["change_pct"].clip(upper=200) / 200 * 20
        + work["relative_volume"].clip(upper=5) / 5 * 10
    ).round(1)
    elite = work[
        (work["momentum_score"] >= 65)
        & (work["liquidity_score"] >= 60)
        & ((work["relative_volume"] >= 1.5) | (work["dollar_volume"] >= 5_000_000))
    ].copy()
    return elite.sort_values(["elite_score", "liquidity_score", "momentum_score"], ascending=False).reset_index(drop=True)


st.title("📡 Live Market Leaders")
st.caption("صفحة مستقلة لاكتشاف أعلى الأسهم ارتفاعًا مباشرة من السوق، بدون استخدام Yahoo كمصدر اكتشاف.")

f1, f2, f3, f4 = st.columns(4)
min_change = f1.number_input("📈 أقل ارتفاع %", min_value=5.0, max_value=500.0, value=40.0, step=5.0)
min_price = f2.number_input("💵 أقل سعر", min_value=0.01, max_value=50.0, value=0.40, step=0.10)
max_price = f3.number_input("💵 أعلى سعر", min_value=0.02, max_value=500.0, value=50.0, step=1.0)
limit = f4.selectbox("عدد المتصدرين", [50, 100, 200, 300, 500], index=3)

if st.button("🔄 جلب المتصدرين الآن", type="primary", width="stretch") or "live_market_leaders" not in st.session_state:
    with st.spinner("جاري فحص السوق الأمريكي مباشرة..."):
        leaders, meta = discover_live_leaders(min_price=min_price, max_price=max_price, min_change=min_change, limit=limit)
        st.session_state["live_market_leaders"] = leaders
        st.session_state["live_market_leaders_meta"] = meta
        st.session_state.pop("live_market_leaders_elite", None)

leaders = st.session_state.get("live_market_leaders", pd.DataFrame())
meta = st.session_state.get("live_market_leaders_meta", {})

s1, s2, s3, s4 = st.columns(4)
s1.metric("🚀 عدد المتصدرين", len(leaders))
s2.metric("🥇 أعلى ارتفاع", f"+{leaders['change_pct'].max():.1f}%" if not leaders.empty else "—")
s3.metric("💧 أعلى حجم", f"{int(leaders['volume'].max()):,}" if not leaders.empty else "—")
s4.metric("📡 المصادر", ", ".join(meta.get("sources", [])) or "غير متاح")

if meta.get("errors"):
    with st.expander("⚠️ ملاحظات المصادر"):
        for err in meta["errors"]:
            st.caption(err)

if leaders.empty:
    st.warning("لم يتم العثور على نتائج ضمن الشروط الحالية. جرّب خفض نسبة الارتفاع أو توسيع نطاق السعر.")
    st.stop()

st.subheader("🚀 المتصدرون الحقيقيون")
st.caption("الترتيب هنا حسب نسبة الارتفاع فقط، من الأعلى إلى الأقل.")
for i, (_, row) in enumerate(leaders.head(60).iterrows(), 1):
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 1.0, 1.1, 1.0, 1.1, 1.2])
        c1.markdown(f"## #{i}")
        c2.markdown(f"## {row['symbol']}")
        c3.metric("📈 الارتفاع", f"+{row['change_pct']:.2f}%")
        c4.metric("السعر", f"${row['price']:.2f}")
        c5.metric("الحجم", f"{int(row['volume']):,}")
        c6.metric("Dollar Volume", f"${row['dollar_volume']/1_000_000:.1f}M")
        company = str(row.get("company", "") or "")
        exchange = str(row.get("exchange", "") or "")
        source = str(row.get("source", "") or "")
        st.caption(f"{company} · {exchange} · المصدر: {source}")

st.divider()
st.subheader("🏆 تحليل نخبة المتصدرين")
st.caption("هذه الخطوة ترسل رموز المتصدرين إلى محلل السيولة والزخم الحالي. الاكتشاف نفسه يبقى من TradingView/Nasdaq وليس Yahoo.")

analysis_limit = st.selectbox("عدد المتصدرين المراد تحليلهم", [20, 40, 60, 100, 150], index=2)
if st.button("🏆 تحليل النخبة الآن", width="stretch"):
    symbols = leaders.head(analysis_limit)["symbol"].tolist()
    snapshot = leaders.head(analysis_limit).rename(columns={
        "price": "market_price",
        "change_pct": "market_change_pct",
        "volume": "market_volume",
    }).copy()
    with st.spinner("تحليل السيولة والزخم للمتصدرين..."):
        analyzed, stats = analyze_gainers(
            symbols,
            threshold=min_change,
            min_price=min_price,
            max_price=max_price,
            market_snapshot=snapshot,
        )
        elite = _build_elite(analyzed)
        st.session_state["live_market_leaders_analyzed"] = analyzed
        st.session_state["live_market_leaders_elite"] = elite
        st.session_state["live_market_leaders_analysis_stats"] = stats

elite = st.session_state.get("live_market_leaders_elite", pd.DataFrame())
if isinstance(elite, pd.DataFrame) and not elite.empty:
    e1, e2, e3 = st.columns(3)
    e1.metric("🏆 أسهم النخبة", len(elite))
    e2.metric("💧 أعلى سيولة", f"{elite['liquidity_score'].max():.0f}/100")
    e3.metric("🚀 أعلى زخم", f"{elite['momentum_score'].max():.0f}/100")
    for i, (_, row) in enumerate(elite.head(25).iterrows(), 1):
        with st.container(border=True):
            a, b, c, d, e, f = st.columns([0.5, 1, 1, 1, 1, 1])
            a.markdown(f"## #{i}")
            b.markdown(f"## {row['symbol']}")
            c.metric("🏆 Elite", f"{row['elite_score']:.1f}")
            d.metric("📈 الارتفاع", f"+{row['change_pct']:.1f}%")
            e.metric("💧 السيولة", f"{row['liquidity_score']:.0f}")
            f.metric("🚀 الزخم", f"{row['momentum_score']:.0f}")
            st.caption(f"RVOL {row['relative_volume']:.2f}x · الحجم {int(row['volume']):,} · Dollar Volume ${row['dollar_volume']:,.0f}")

with st.expander("📋 البيانات الخام"):
    st.dataframe(leaders, width="stretch", hide_index=True)
