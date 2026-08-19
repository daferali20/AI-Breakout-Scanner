"""المحفزات والتفسيرات المرتبطة بالفرص — قراءة قابلة للتفسير من نتائج المسح."""
import pandas as pd
import streamlit as st
from backend.results_store import get_scan


def _num(row, name, default=0.0):
    try:
        return float(row.get(name, default) or default)
    except (TypeError, ValueError):
        return default


def _catalysts(row):
    items = []
    rvol = _num(row, "relative_volume", 0)
    momentum = _num(row, "momentum_score", 0)
    liquidity = _num(row, "liquidity_score", 0)
    breakout = _num(row, "breakout_probability", 0)
    confirmation = _num(row, "confirmation_score", 0)
    risk = _num(row, "false_breakout_risk", 100)
    change = _num(row, "change_pct", row.get("change", 0) or 0)

    if rvol >= 3:
        items.append(("🔥", "حجم تداول استثنائي", f"Relative Volume = {rvol:.2f}x"))
    elif rvol >= 2:
        items.append(("💧", "نشاط سيولة مرتفع", f"Relative Volume = {rvol:.2f}x"))
    if momentum >= 80:
        items.append(("🚀", "زخم قوي", f"Momentum = {momentum:.0f}/100"))
    elif momentum >= 70:
        items.append(("📈", "زخم إيجابي", f"Momentum = {momentum:.0f}/100"))
    if breakout >= 85:
        items.append(("⚡", "احتمال اختراق مرتفع", f"Breakout = {breakout:.0f}%"))
    if confirmation >= 80:
        items.append(("✅", "تأكيد قوي", f"Confirmation = {confirmation:.0f}/100"))
    if liquidity >= 80:
        items.append(("💎", "سيولة قوية", f"Liquidity = {liquidity:.0f}/100"))
    if change >= 5:
        items.append(("🟢", "تسارع سعري", f"التغير = {change:.2f}%"))
    if risk <= 20:
        items.append(("🛡️", "خطر اختراق كاذب منخفض", f"Risk = {risk:.0f}%"))
    return items


def render():
    st.title("📰 المحفزات والفرص")
    st.caption("تحويل إشارات المسح إلى محفزات قابلة للفهم. الأخبار الخارجية لا تُفترض ما لم تكن محفوظة ضمن نتيجة المسح.")
    df = get_scan().get("scan_results_all", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("لا توجد نتائج محفوظة حاليًا. شغّل المسح من لوحة التحكم.")
        return

    work = df.copy()
    if "opportunity_score" not in work:
        work["opportunity_score"] = 0.0
    work["opportunity_score"] = pd.to_numeric(work["opportunity_score"], errors="coerce").fillna(0)

    strong = work[work["opportunity_score"] >= 80]
    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 فرص قوية", len(strong))
    c2.metric("🚀 محفزات تقنية", sum(bool(_catalysts(r)) for _, r in work.iterrows()))
    c3.metric("🏆 أعلى Score", f"{work['opportunity_score'].max():.1f}")

    st.subheader("🏆 أهم الفرص والمحـفزات")
    for _, row in work.sort_values("opportunity_score", ascending=False).head(15).iterrows():
        symbol = str(row.get("symbol", "—"))
        score = _num(row, "opportunity_score")
        catalysts = _catalysts(row)
        with st.container(border=True):
            left, mid, right = st.columns([3, 4, 2])
            with left:
                st.markdown(f"### {symbol}")
                st.metric("Opportunity Score", f"{score:.1f}/100")
            with mid:
                if catalysts:
                    for icon, title, detail in catalysts[:6]:
                        st.write(f"{icon} **{title}** — {detail}")
                else:
                    st.caption("لا توجد محفزات تقنية قوية وفق البيانات الحالية.")
            with right:
                st.metric("Confidence", f"{_num(row, 'confidence'):.0f}/100")
                st.metric("Risk", f"{_num(row, 'false_breakout_risk'):.0f}%")
            st.caption(f"المرحلة: {row.get('phase', 'WATCH')} • الإشارة: {row.get('signal', 'WATCH')}")

    st.subheader("📌 ملاحظة")
    st.info("هذه الصفحة تميز بين المحفزات المستنتجة من بيانات المسح وبين الأخبار. لا يتم اعتبار خبر أو حدث مؤثر محفزًا إلا إذا كان مصدره موجودًا في بيانات النظام.")
