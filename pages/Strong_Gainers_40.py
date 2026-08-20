"""🚀 Independent +40% gainers dashboard."""
from __future__ import annotations
import streamlit as st
from backend.gainers_universe import get_universe, universe_status
from backend.strong_gainers import analyze_gainers, discover_strong_gainers

st.set_page_config(page_title="الأسهم الصاعدة +40%", page_icon="🚀", layout="wide")
st.title("🚀 الأسهم الأكثر ارتفاعًا +40%")
st.caption("ماسح مستقل للارتفاعات الاستثنائية؛ نتائجه لا تدخل في قائمة المراقبة أو السجل التاريخي.")

status = universe_status()
u1, u2, u3 = st.columns(3)
u1.metric("🇺🇸 الكون المستقل", f"{status['count']:,} رمز")
u2.metric("💾 التخزين المؤقت", "6 ساعات")
u3.metric("📡 المصدر", "Nasdaq / NYSE / AMEX")

c1, c2, c3 = st.columns([1, 1, 1])
auto = c1.toggle("🤖 اكتشاف تلقائي", value=True)
manual = c2.text_input("🔎 سهم/رموز إضافية", placeholder="NVDA, AMD, PLTR")
limit = c3.selectbox("حجم الكون", [150, 300, 600, 1000, 1500], index=1, format_func=lambda x: f"{x:,} رمز")

if st.button("🔄 تحديث الأسهم +40%", type="primary", use_container_width=True):
    with st.spinner("جاري فحص السوق على دفعات آمنة وتحليل الزخم والسيولة..."):
        universe = get_universe(limit)
        if auto:
            df = discover_strong_gainers(limit=limit)
        else:
            symbols = [x.strip().upper() for x in manual.replace("\n", ",").split(",") if x.strip()]
            df = analyze_gainers(symbols or list(universe))
        st.session_state["strong_gainers_40"] = df
        st.session_state["strong_gainers_40_universe"] = len(universe)

if "strong_gainers_40" not in st.session_state and auto:
    with st.spinner("جاري أول اكتشاف تلقائي على الكون المستقل..."):
        st.session_state["strong_gainers_40"] = discover_strong_gainers(limit=limit)
        st.session_state["strong_gainers_40_universe"] = len(get_universe(limit))

df = st.session_state.get("strong_gainers_40")
if df is None:
    st.info("اضغط «تحديث الأسهم +40%» لبدء الفحص.")
    st.stop()
if df.empty:
    st.warning("لم يتم العثور على سهم ارتفع 40% أو أكثر ضمن البيانات المتاحة حاليًا. جرّب توسيع الكون أو إعادة التحديث.")
    st.caption(f"تم فحص نحو {st.session_state.get('strong_gainers_40_universe', limit):,} رمزًا. عدم ظهور نتائج لا يعني بالضرورة عدم وجود ارتفاعات في السوق إذا كان مصدر البيانات لا يعيد بعض الرموز.")
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
        st.caption(f"السعر: ${row['price']:.2f} · الحجم: {int(row['volume']):,} · Dollar Volume: ${row['dollar_volume']:,.0f} · RSI: {row['rsi']:.1f} · Gainer Score: {row['gainer_score']:.1f}")

with st.expander("عرض البيانات الكاملة"):
    st.dataframe(df, use_container_width=True, hide_index=True)
