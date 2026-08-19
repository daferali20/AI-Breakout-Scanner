"""تحليل سهم منفرد اعتمادًا على آخر نتائج المسح."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("📊 تحليل السهم")
    st.caption("تحليل متعمق لفرصة موجودة في آخر مسح محفوظ.")
    data = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(data, pd.DataFrame) or data.empty:
        st.info("شغّل المسح من لوحة التحكم أولًا.")
        return
    symbols = data["symbol"].astype(str).tolist()
    symbol = st.selectbox("اختر السهم", symbols)
    row = data[data["symbol"].astype(str) == symbol].iloc[0]
    score = float(row.get("opportunity_score", row.get("setup_score", 0)) or 0)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opportunity Score", f"{score:.1f}/100")
    c2.metric("Confidence", f"{float(row.get('confirmation_score', 0) or 0):.0f}/100")
    c3.metric("Breakout", f"{float(row.get('breakout_probability', 0) or 0):.0f}%")
    c4.metric("False Breakout Risk", f"{float(row.get('false_breakout_risk', 0) or 0):.0f}%")
    st.markdown("---")
    a, b, c, d = st.columns(4)
    a.metric("Momentum", f"{float(row.get('momentum_score', 0) or 0):.0f}")
    b.metric("Liquidity", f"{float(row.get('liquidity_score', 0) or 0):.0f}")
    c.metric("Trend", f"{float(row.get('trend_score', 0) or 0):.0f}")
    d.metric("Relative Volume", f"{float(row.get('relative_volume', 1) or 1):.2f}x")
    st.subheader(f"💡 لماذا {symbol}؟")
    st.info(str(row.get("explanation", "لا يوجد تفسير محفوظ لهذا السهم.")))
    st.subheader("🎯 المستويات")
    p1, p2 = st.columns(2)
    p1.metric("السعر الحالي", f"${float(row.get('price', 0) or 0):.2f}")
    p2.metric("الهدف", f"${float(row.get('target', 0) or 0):.2f}")
    st.caption(f"المرحلة: {row.get('phase', 'WATCH')}  •  الإشارة: {row.get('signal', 'WATCH')}  •  التقييم: {row.get('signal_quality', 'Watch')}")
