"""📚 Historical opportunities - previously extracted stocks."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.results_store import get_scan

st.set_page_config(page_title="تم استخراجها سابقًا", page_icon="📚", layout="wide")

st.title("📚 تم استخراجها سابقًا")
st.caption("سجل الفرص التي اكتشفها النظام سابقًا ويتابع تغير حالتها.")

state = get_scan()
history = state.get("historical_opportunities", pd.DataFrame())

if not isinstance(history, pd.DataFrame) or history.empty:
    st.info("لا توجد فرص محفوظة حتى الآن. شغّل المسح من لوحة التحكم أولًا.")
    st.stop()

df = history.copy()

# Normalize common numeric fields without assuming a fixed scanner schema.
for col in ["current_score", "best_score", "current_confidence", "times_detected", "risk_reward", "current_price"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

c1, c2, c3, c4 = st.columns(4)
c1.metric("📚 إجمالي الفرص", len(df))
c2.metric("🔥 قوية", int((df.get("current_score", pd.Series(dtype=float)) >= 80).sum()))
c3.metric("🔁 متكررة", int((df.get("times_detected", pd.Series(dtype=float)) >= 2).sum()))
c4.metric("🚀 مؤكدة", int((df.get("current_stage", pd.Series(dtype=str)) == "CONFIRMED").sum()))

st.divider()

f1, f2, f3 = st.columns([2, 1, 1])
query = f1.text_input("🔎 البحث عن سهم", placeholder="مثال: NVDA")
statuses = sorted(df.get("status", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
status = f2.selectbox("الحالة", ["الكل"] + statuses)
stage_values = sorted(df.get("current_stage", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
stage = f3.selectbox("المرحلة", ["الكل"] + stage_values)

filtered = df.copy()
if query:
    mask = filtered.astype(str).apply(lambda s: s.str.contains(query.strip(), case=False, na=False)).any(axis=1)
    filtered = filtered[mask]
if status != "الكل" and "status" in filtered:
    filtered = filtered[filtered["status"].astype(str) == status]
if stage != "الكل" and "current_stage" in filtered:
    filtered = filtered[filtered["current_stage"].astype(str) == stage]

if "current_score" in filtered:
    filtered = filtered.sort_values("current_score", ascending=False)

st.subheader(f"الفرص ({len(filtered)})")

for _, row in filtered.head(50).iterrows():
    ticker = str(row.get("ticker", row.get("symbol", "—")))
    current = row.get("current_score", 0)
    best = row.get("best_score", 0)
    stage_value = str(row.get("current_stage", "WATCH"))
    status_value = str(row.get("status", "PERSISTENT"))
    detected = int(row.get("times_detected", 0) or 0)
    rr = row.get("risk_reward", 0)
    price = row.get("current_price", 0)

    with st.container(border=True):
        a, b, c, d, e = st.columns([1.3, 1.2, 1.2, 1.2, 1.2])
        a.markdown(f"### {ticker}")
        b.metric("Score", f"{float(current):.1f}", delta=f"Best {float(best):.1f}")
        c.metric("الظهور", detected)
        d.metric("R:R", f"{float(rr):.2f}")
        e.metric("السعر", f"${float(price):.2f}" if pd.notna(price) and float(price) else "—")
        st.write(f"**الحالة:** {status_value}  ·  **المرحلة:** {stage_value}")
        if row.get("first_seen") or row.get("last_seen"):
            st.caption(f"أول ظهور: {row.get('first_seen', '—')}  |  آخر ظهور: {row.get('last_seen', '—')}")

st.divider()

with st.expander("عرض البيانات الكاملة"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
