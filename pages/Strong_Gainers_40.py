"""🚀 Independent +40% gainers page."""
from __future__ import annotations
import streamlit as st
from backend.strong_gainers import analyze_gainers

st.set_page_config(page_title="الأسهم الصاعدة +40%", page_icon="🚀", layout="wide")
st.title("🚀 الأسهم الأكثر ارتفاعًا +40%")
st.caption("صفحة مستقلة لا تخلط نتائجها مع قائمة المراقبة أو الفرص التاريخية.")

symbols_text = st.text_area("قائمة الأسهم المراد فحصها", value="NVDA, AMD, PLTR, TSLA, SMCI, HOOD, MARA, CLSK, ASTS, SOFI", height=70)
symbols = [x.strip().upper() for x in symbols_text.replace("\n", ",").split(",") if x.strip()]

if st.button("🔄 فحص الأسهم +40%", type="primary", use_container_width=True):
    with st.spinner("جاري فحص الارتفاع والزخم والسيولة..."):
        st.session_state["strong_gainers_40"] = analyze_gainers(symbols)

df = st.session_state.get("strong_gainers_40")
if df is None:
    st.info("أدخل الأسهم ثم اضغط «فحص الأسهم +40%». هذه الصفحة مستقلة عن القوائم الأخرى.")
    st.stop()

if df.empty:
    st.warning("لم يتم العثور على سهم ارتفع 40% أو أكثر ضمن المجموعة الحالية.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
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
        st.caption(f"السعر: ${row['price']:.2f} · الحجم: {int(row['volume']):,} · Dollar Volume: ${row['dollar_volume']:,.0f} · RSI: {row['rsi']:.1f} · Gainer Score: {row['gainer_score']:.1f}")

with st.expander("عرض البيانات الكاملة"):
    st.dataframe(df, use_container_width=True, hide_index=True)
