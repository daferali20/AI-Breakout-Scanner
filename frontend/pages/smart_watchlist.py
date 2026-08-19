"""قائمة مراقبة ذكية مشتقة من آخر مسح موحد."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("⭐ قائمة المراقبة الذكية")
    st.caption("ترتيب ديناميكي يجمع جودة الفرصة والثقة والزخم والسيولة والإشارات المتقدمة.")
    snapshot = get_scan()
    df = snapshot.get("smart_watchlist", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد قائمة مراقبة بعد. شغّل المسح من لوحة التحكم أولًا.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⭐ في القائمة", len(df))
    c2.metric("🔥 HOT", int((df.get("watch_status", pd.Series(dtype=str)) == "HOT").sum()))
    c3.metric("🟢 PRIORITY", int((df.get("watch_status", pd.Series(dtype=str)) == "PRIORITY").sum()))
    c4.metric("🧠 إشارات متقدمة", int((pd.to_numeric(df.get("advanced_signal_count", 0), errors="coerce") > 0).sum()))

    st.subheader("🏆 ترتيب المراقبة")
    columns = [c for c in [
        "symbol", "price", "watch_status", "watchlist_score", "enhanced_opportunity_score",
        "confidence_score", "momentum_score", "liquidity_score", "relative_volume",
        "advanced_signals", "false_breakout_risk", "phase"
    ] if c in df.columns]
    st.dataframe(df[columns], width="stretch", hide_index=True)

    st.subheader("🎯 أعلى 5 أسهم")
    for _, row in df.head(5).iterrows():
        with st.container(border=True):
            a, b, c, d, e = st.columns(5)
            a.metric("السهم", str(row.get("symbol", "—")))
            b.metric("Watch Score", f"{float(row.get('watchlist_score', 0)):.1f}")
            c.metric("Opportunity", f"{float(row.get('enhanced_opportunity_score', row.get('opportunity_score', 0))):.1f}")
            d.metric("RVOL", f"{float(row.get('relative_volume', 1)):.2f}x")
            e.metric("Risk", f"{float(row.get('false_breakout_risk', 0)):.0f}%")
            st.caption(f"{row.get('watch_status', 'WATCH')} • {row.get('advanced_signals', 'لا توجد إشارة متقدمة')} • المرحلة: {row.get('phase', 'WATCH')}")

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ تصدير قائمة المراقبة CSV", csv, "smart_watchlist.csv", "text/csv", width="stretch")
