"""🚀 Independent +40% gainers dashboard."""
from __future__ import annotations
import streamlit as st
from backend.gainers_universe import get_universe, universe_status
from backend.strong_gainers import MIN_PRICE, MAX_PRICE, analyze_gainers, discover_strong_gainers

st.set_page_config(page_title="الأسهم الصاعدة +40%", page_icon="🚀", layout="wide")
st.title("🚀 الأسهم الأكثر ارتفاعًا +40%")
st.caption("ماسح مستقل؛ لا يضيف نتائجه إلى القوائم الأخرى.")

status = universe_status()
u1, u2, u3 = st.columns(3)
u1.metric("🇺🇸 الكون المستقل", f"{status['count']:,} رمز")
u2.metric("💾 التخزين المؤقت", "6 ساعات")
u3.metric("📡 المصدر", "Nasdaq / NYSE / AMEX")

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
auto = c1.toggle("🤖 اكتشاف تلقائي", value=True)
manual = c2.text_input("🔎 سهم/رموز إضافية", placeholder="NVDA, AMD, PLTR")
limit = c3.selectbox("حجم الكون", [150, 300, 600, 1000, 1500], index=1, format_func=lambda x: f"{x:,} رمز")
price_range = c4.selectbox("💵 نطاق السعر", ["$0.40 – $50", "$0.40 – $10", "$1 – $50", "مخصص"], index=0)
if price_range == "$0.40 – $10": min_price, max_price = 0.40, 10.0
elif price_range == "$1 – $50": min_price, max_price = 1.0, 50.0
elif price_range == "مخصص":
    p1, p2 = st.columns(2)
    min_price = p1.number_input("أقل سعر", min_value=0.01, value=0.40, step=0.10)
    max_price = p2.number_input("أعلى سعر", min_value=0.02, value=50.00, step=1.00)
else: min_price, max_price = MIN_PRICE, MAX_PRICE

if st.button("🔄 تحديث الأسهم +40%", type="primary", use_container_width=True):
    with st.spinner("جاري فحص السوق وتحليل الارتفاع والزخم والسيولة..."):
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
    d1,d2,d3,d4 = st.columns(4)
    d1.metric("الرموز المطلوبة", f"{stats.get('requested', 0):,}")
    d2.metric("بيانات صالحة", f"{stats.get('with_data', 0):,}")
    d3.metric("ضمن السعر", f"{stats.get('price_range', 0):,}")
    d4.metric("+40%", f"{stats.get('above_threshold', 0):,}")

if df.empty:
    st.warning(f"لم يتم العثور على سهم +40% ضمن نطاق ${min_price:.2f} إلى ${max_price:.2f} في الكون المفحوص.")
    st.caption("هذه النتيجة مستقلة عن قوائم الفرص والمراقبة والسجل التاريخي.")
    st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("🚀 الأسهم +40%", len(df))
c2.metric("🔥 زخم قوي", int((df["momentum_score"] >= 70).sum()))
c3.metric("💧 سيولة قوية", int((df["liquidity_score"] >= 70).sum()))
c4.metric("⚡ RVOL مرتفع", int((df["relative_volume"] >= 2).sum()))
st.divider()

for _, row in df.head(30).iterrows():
    with st.container(border=True):
        a,b,c,d,e,f = st.columns([1.2,1,1,1,1,1.4])
        a.markdown(f"### {row['symbol']}")
        b.metric("الارتفاع", f"+{row['change_pct']:.1f}%")
        c.metric("الزخم", f"{row['momentum_score']:.0f}/100")
        d.metric("السيولة", f"{row['liquidity_score']:.0f}/100")
        e.metric("RVOL", f"{row['relative_volume']:.2f}x")
        f.metric("قوة الارتفاع", row["strength"])
        st.caption(f"السعر: ${row['price']:.2f} · الفترة: {row['period']} · الحجم: {int(row['volume']):,} · Dollar Volume: ${row['dollar_volume']:,.0f} · RSI: {row['rsi']:.1f} · Gainer Score: {row['gainer_score']:.1f}")

with st.expander("عرض البيانات الكاملة"):
    st.dataframe(df, use_container_width=True, hide_index=True)
