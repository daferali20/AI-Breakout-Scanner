"""صفحة السيولة والزخم."""
import pandas as pd
import plotly.express as px
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("💧 السيولة والزخم")
    st.caption("اكتشاف النشاط غير الاعتيادي من نتائج آخر مسح.")
    df = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد بيانات. شغّل المسح أولًا.")
        return
    work = df.copy()
    for col in ["relative_volume", "momentum_score", "liquidity_score", "opportunity_score"]:
        if col in work:
            work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)
    top = work.sort_values("relative_volume", ascending=False).head(15)
    st.subheader("🔥 أعلى نشاط حجمي")
    st.dataframe(top[[c for c in ["symbol", "relative_volume", "momentum_score", "liquidity_score", "opportunity_score"] if c in top.columns]], width="stretch", hide_index=True)
    if "relative_volume" in top and "momentum_score" in top:
        fig = px.scatter(top, x="relative_volume", y="momentum_score", text="symbol", size="liquidity_score" if "liquidity_score" in top else None, title="السيولة مقابل الزخم")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, width="stretch")
    st.subheader("📈 أكثر الأسهم نشاطًا")
    st.dataframe(work.sort_values("momentum_score", ascending=False).head(20), width="stretch", hide_index=True)
