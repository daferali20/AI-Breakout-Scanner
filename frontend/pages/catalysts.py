"""المحفزات والتفسيرات المرتبطة بالفرص."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("📰 المحفزات والفرص")
    st.caption("ملخص الأسباب المحفزة لكل فرصة محفوظة في آخر مسح.")
    df = get_scan().get("scan_results", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد فرص محفوظة حاليًا. شغّل المسح من لوحة التحكم.")
        return
    for _, row in df.head(15).iterrows():
        symbol = str(row.get("symbol", "—"))
        score = float(row.get("opportunity_score", row.get("setup_score", 0)) or 0)
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"### {symbol}")
                st.write(str(row.get("explanation", "لا يوجد تفسير محفوظ.")))
                st.caption(f"المرحلة: {row.get('phase', 'WATCH')} • الإشارة: {row.get('signal', 'WATCH')} • الخطر: {float(row.get('false_breakout_risk', 0) or 0):.0f}%")
            with right:
                st.metric("Score", f"{score:.1f}")
