"""مستكشف السوق: عرض جميع نتائج المسح مع فلاتر تفاعلية."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("🔎 مستكشف السوق")
    st.caption("استكشف نتائج آخر مسح محفوظ بدون إعادة طلب بيانات Yahoo.")
    data = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(data, pd.DataFrame) or data.empty:
        st.info("لا توجد نتائج محفوظة. شغّل المسح من لوحة التحكم أولًا.")
        return
    df = data.copy()
    c1, c2, c3, c4 = st.columns(4)
    min_score = c1.slider("🎯 الحد الأدنى للفرصة", 0, 100, 40, 5)
    min_rvol = c2.number_input("💧 أقل Relative Volume", 0.0, 20.0, 1.0, 0.1)
    phases = sorted(df.get("phase", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    phase = c3.selectbox("🚀 المرحلة", ["الكل"] + phases)
    search = c4.text_input("🔍 رمز السهم", "").strip().upper()
    score_col = "opportunity_score" if "opportunity_score" in df else "setup_score"
    df[score_col] = pd.to_numeric(df[score_col], errors="coerce").fillna(0)
    df["relative_volume"] = pd.to_numeric(df.get("relative_volume", 1), errors="coerce").fillna(0)
    view = df[(df[score_col] >= min_score) & (df["relative_volume"] >= min_rvol)]
    if phase != "الكل":
        view = view[view["phase"].astype(str) == phase]
    if search:
        view = view[view["symbol"].astype(str).str.contains(search, na=False)]
    st.metric("النتائج المطابقة", len(view))
    cols = [c for c in ["symbol", "price", score_col, "confirmation_score", "breakout_probability", "false_breakout_risk", "relative_volume", "phase", "signal_quality"] if c in view.columns]
    st.dataframe(view.sort_values(score_col, ascending=False)[cols], width="stretch", hide_index=True)
