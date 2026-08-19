"""مستكشف الإشارات المتقدمة من آخر مسح موحد."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("🧠 الإشارات المتقدمة")
    st.caption("Squeeze • Volume Anomaly • Relative Strength • Breakout Retest — بدون إعادة جلب بيانات Yahoo.")
    snapshot = get_scan()
    df = snapshot.get("ranked_results", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد نتائج بعد. شغّل المسح أولًا.")
        return

    flags = {
        "squeeze_signal": "⚡ Squeeze",
        "volume_anomaly_signal": "💧 Volume Anomaly",
        "relative_strength_signal": "💪 Relative Strength",
        "breakout_retest_signal": "🔄 Breakout Retest",
    }
    counts = {}
    for key, label in flags.items():
        counts[label] = int(pd.to_numeric(df.get(key, 0), errors="coerce").fillna(0).sum())

    cols = st.columns(4)
    for col, (label, count) in zip(cols, counts.items()):
        col.metric(label, count)

    selected = st.multiselect("🔎 الإشارات المطلوب عرضها", list(flags.values()), default=list(flags.values()))
    selected_keys = [k for k, v in flags.items() if v in selected]
    if not selected_keys:
        st.info("اختر إشارة واحدة على الأقل.")
        return

    mask = pd.Series(False, index=df.index)
    for key in selected_keys:
        mask |= pd.to_numeric(df.get(key, 0), errors="coerce").fillna(0).astype(bool)
    result = df.loc[mask].copy()
    result = result.sort_values(["advanced_signal_count", "enhanced_opportunity_score"], ascending=False)

    columns = [c for c in [
        "symbol", "price", "advanced_signal_count", "advanced_signal_score", "advanced_signals",
        "enhanced_opportunity_score", "opportunity_score", "confidence_score", "relative_volume",
        "momentum_score", "false_breakout_risk", "phase"
    ] if c in result.columns]
    st.subheader("🏆 الأسهم ذات الإشارات المتقدمة")
    st.dataframe(result[columns], width="stretch", hide_index=True)

    st.download_button("⬇️ تصدير الإشارات CSV", result.to_csv(index=False).encode("utf-8-sig"), "advanced_signals.csv", "text/csv", width="stretch")
