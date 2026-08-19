"""صفحة السيولة والزخم — محرك اكتشاف للإشارات غير الاعتيادية."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def _num(row, name, default=0.0):
    try:
        return float(row.get(name, default) or default)
    except (TypeError, ValueError):
        return default


def _signal(row):
    rvol = _num(row, "relative_volume", 1)
    mom = _num(row, "momentum_score")
    liq = _num(row, "liquidity_score")
    conf = _num(row, "confirmation_score")
    risk = _num(row, "false_breakout_risk", 50)
    score = min(100, max(0, 0.30 * min(rvol / 3, 1) * 100 + 0.30 * mom + 0.20 * liq + 0.15 * conf + 0.05 * (100 - risk)))
    if rvol >= 3 and mom >= 80 and liq >= 75:
        label = "🔥 تدفق استثنائي"
    elif rvol >= 2 and mom >= 75:
        label = "🟢 دخول سيولة قوي"
    elif rvol >= 1.5 and mom >= 65:
        label = "🟡 نشاط متزايد"
    else:
        label = "⚪ نشاط عادي"
    return score, label


def render():
    st.title("💧 السيولة والزخم")
    st.caption("اكتشاف النشاط غير الاعتيادي من نتائج آخر مسح، دون إعادة طلب بيانات Yahoo.")
    df = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد بيانات. شغّل المسح من لوحة التحكم أولًا.")
        return
    work = df.copy()
    for col in ["relative_volume", "momentum_score", "liquidity_score", "opportunity_score", "confirmation_score", "false_breakout_risk"]:
        if col not in work:
            work[col] = 0.0
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)

    work["flow_score"], work["flow_signal"] = zip(*work.apply(_signal, axis=1))

    strong_flow = work[(work["relative_volume"] >= 2) & (work["momentum_score"] >= 75)].copy()
    exceptional = work[(work["relative_volume"] >= 3) & (work["momentum_score"] >= 80) & (work["liquidity_score"] >= 75)].copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💧 RVOL ≥ 2x", int((work["relative_volume"] >= 2).sum()))
    c2.metric("📈 زخم ≥ 75", int((work["momentum_score"] >= 75).sum()))
    c3.metric("🔥 تدفق استثنائي", len(exceptional))
    c4.metric("🎯 فرص سيولة+زخم", len(strong_flow))

    st.subheader("🔥 أقوى إشارات تدفق السيولة")
    top = work.sort_values(["flow_score", "opportunity_score"], ascending=False).head(15)
    cols = [c for c in ["symbol", "price", "flow_score", "flow_signal", "relative_volume", "liquidity_score", "momentum_score", "opportunity_score", "phase"] if c in top.columns]
    st.dataframe(top[cols], width="stretch", hide_index=True)

    st.subheader("🚀 الأسهم ذات النشاط غير الاعتيادي")
    momentum = work.sort_values(["momentum_score", "relative_volume"], ascending=False).head(15)
    cols = [c for c in ["symbol", "price", "momentum_score", "relative_volume", "liquidity_score", "confirmation_score", "false_breakout_risk", "opportunity_score", "phase"] if c in momentum.columns]
    st.dataframe(momentum[cols], width="stretch", hide_index=True)

    st.subheader("🏆 أفضل الفرص التي تجمع السيولة والزخم")
    leaders = strong_flow.sort_values(["flow_score", "opportunity_score"], ascending=False).head(5)
    if leaders.empty:
        st.info("لا توجد حاليًا أسهم تجمع بين حجم غير اعتيادي وزخم قوي.")
    else:
        for _, row in leaders.iterrows():
            symbol = str(row.get("symbol", "—"))
            with st.container(border=True):
                a, b, c, d, e = st.columns(5)
                a.metric("السهم", symbol)
                b.metric("قوة التدفق", f"{_num(row, 'flow_score'):.0f}/100")
                c.metric("RVOL", f"{_num(row, 'relative_volume'):.2f}x")
                d.metric("الزخم", f"{_num(row, 'momentum_score'):.0f}/100")
                e.metric("السيولة", f"{_num(row, 'liquidity_score'):.0f}/100")
                st.caption(f"{row.get('flow_signal', '—')} • المرحلة: {row.get('phase', 'WATCH')} • فرصة: {_num(row, 'opportunity_score'):.1f}/100 • خطر الاختراق الكاذب: {_num(row, 'false_breakout_risk'):.0f}%")
