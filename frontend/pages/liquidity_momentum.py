"""صفحة السيولة والزخم — بدون رسوم بيانية، تركيز على الإشارات القابلة للقراءة."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def _num(row, name, default=0.0):
    try:
        return float(row.get(name, default) or default)
    except (TypeError, ValueError):
        return default


def render():
    st.title("💧 السيولة والزخم")
    st.caption("اكتشاف النشاط غير الاعتيادي من نتائج آخر مسح، دون إعادة طلب بيانات Yahoo.")
    df = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد بيانات. شغّل المسح من لوحة التحكم أولًا.")
        return
    work = df.copy()
    for col in ["relative_volume", "momentum_score", "liquidity_score", "opportunity_score", "confirmation_score", "false_breakout_risk"]:
        if col in work:
            work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)

    c1, c2, c3 = st.columns(3)
    c1.metric("💧 RVOL مرتفع", int((work.get("relative_volume", pd.Series(dtype=float)) >= 2).sum()))
    c2.metric("📈 زخم قوي", int((work.get("momentum_score", pd.Series(dtype=float)) >= 75).sum()))
    c3.metric("🚀 تأكيد قوي", int((work.get("confirmation_score", pd.Series(dtype=float)) >= 75).sum()))

    st.subheader("🔥 أقوى دخول سيولة")
    top = work.sort_values(["relative_volume", "liquidity_score"], ascending=False).head(15)
    cols = [c for c in ["symbol", "price", "relative_volume", "liquidity_score", "momentum_score", "confirmation_score", "opportunity_score", "phase"] if c in top.columns]
    st.dataframe(top[cols], width="stretch", hide_index=True)

    st.subheader("🚀 نشاط الزخم")
    momentum = work.sort_values("momentum_score", ascending=False).head(15)
    cols = [c for c in ["symbol", "price", "momentum_score", "relative_volume", "opportunity_score", "false_breakout_risk", "phase"] if c in momentum.columns]
    st.dataframe(momentum[cols], width="stretch", hide_index=True)

    st.subheader("🧭 قراءة سريعة")
    leaders = work[(work["relative_volume"] >= 2) & (work["momentum_score"] >= 75)].sort_values("opportunity_score", ascending=False).head(5)
    if leaders.empty:
        st.info("لا توجد حاليًا أسهم تجمع بين حجم غير اعتيادي وزخم قوي.")
    else:
        for _, row in leaders.iterrows():
            symbol = str(row.get("symbol", "—"))
            with st.container(border=True):
                a, b, c, d = st.columns(4)
                a.metric("السهم", symbol)
                b.metric("RVOL", f"{_num(row, 'relative_volume'):.2f}x")
                c.metric("الزخم", f"{_num(row, 'momentum_score'):.0f}/100")
                d.metric("السيولة", f"{_num(row, 'liquidity_score'):.0f}/100")
                st.caption(f"المرحلة: {row.get('phase', 'WATCH')} • درجة الفرصة: {_num(row, 'opportunity_score'):.1f}")
