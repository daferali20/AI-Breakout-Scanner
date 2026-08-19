"""صفحة التنبيهات الذكية المبنية على آخر نتائج المسح."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def render():
    st.title("🔔 التنبيهات الذكية")
    st.caption("تنبيهات مركزة على التحولات المهمة بدل التنبيه على كل حركة سعرية.")
    snapshot = get_scan()
    alerts = snapshot.get("alerts", [])
    if not alerts:
        st.info("لا توجد تنبيهات جديدة حاليًا. شغّل المسح لتحديث المحرك.")
        return

    high = sum(1 for x in alerts if x.get("priority") == "HIGH")
    medium = sum(1 for x in alerts if x.get("priority") == "MEDIUM")
    c1, c2, c3 = st.columns(3)
    c1.metric("🔔 إجمالي التنبيهات", len(alerts))
    c2.metric("🔥 عالية الأولوية", high)
    c3.metric("🟡 متوسطة الأولوية", medium)

    labels = {"ELITE": "🏆 Elite", "VOLUME": "💧 Volume", "BREAKOUT": "🚀 Breakout", "RETEST": "🔄 Retest", "SQUEEZE": "⚡ Squeeze"}
    for alert in alerts:
        priority = alert.get("priority", "MEDIUM")
        with st.container(border=True):
            a, b, c = st.columns([1, 2, 5])
            a.markdown(f"### {alert.get('symbol', '—')}")
            b.markdown(f"**{labels.get(alert.get('type'), alert.get('type', 'ALERT'))}**")
            c.write(alert.get("message", ""))
            st.caption(f"الأولوية: {priority}")

    st.download_button(
        "⬇️ تصدير التنبيهات CSV",
        pd.DataFrame(alerts).to_csv(index=False).encode("utf-8-sig"),
        "smart_alerts.csv",
        "text/csv",
        width="stretch",
    )
