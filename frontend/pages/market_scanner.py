"""مستكشف السوق الاحترافي.

يعرض نتائج آخر مسح محفوظ ويتيح للمستخدم تضييق القائمة إلى الفرص الأقوى
بدون إعادة طلب بيانات من Yahoo Finance.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.results_store import get_scan


_SCORE_FIELDS = (
    "opportunity_score",
    "setup_score",
    "confirmation_score",
    "breakout_probability",
    "false_breakout_risk",
    "relative_volume",
    "momentum_score",
    "liquidity_score",
)


def _number(df: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    """Return a numeric column safely, even when the scanner omitted it."""
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").fillna(default)


def _score_column(df: pd.DataFrame) -> str:
    for name in ("opportunity_score", "setup_score", "score"):
        if name in df.columns:
            return name
    df["opportunity_score"] = 0.0
    return "opportunity_score"


def _quality_label(row: pd.Series, score_col: str) -> str:
    score = float(row.get(score_col, 0) or 0)
    confidence = float(row.get("confirmation_score", 0) or 0)
    risk = float(row.get("false_breakout_risk", 100) or 100)

    if score >= 85 and confidence >= 75 and risk <= 25:
        return "🔥 استثنائية"
    if score >= 75 and confidence >= 65 and risk <= 35:
        return "🟢 قوية"
    if score >= 60:
        return "🟡 واعدة"
    return "⚪ مراقبة"


def _apply_preset(df: pd.DataFrame, preset: str, score_col: str) -> pd.DataFrame:
    if preset == "🔥 أفضل الفرص":
        return df[df[score_col] >= 75]
    if preset == "🚀 اختراقات محتملة":
        return df[df["breakout_probability"] >= 70]
    if preset == "💧 سيولة غير اعتيادية":
        return df[df["relative_volume"] >= 2]
    if preset == "📈 زخم قوي":
        return df[df["momentum_score"] >= 70]
    if preset == "🛡️ مخاطر أقل":
        return df[df["false_breakout_risk"] <= 30]
    return df


def render() -> None:
    st.title("🔎 مستكشف السوق")
    st.caption("ابحث داخل نتائج آخر مسح محفوظ، ورتّب الفرص حسب القوة والسيولة والتأكيد دون إعادة طلب Yahoo Finance.")

    snapshot = get_scan()
    data = snapshot.get("scan_results_all", pd.DataFrame())

    if not isinstance(data, pd.DataFrame) or data.empty:
        st.info("لا توجد نتائج محفوظة. شغّل المسح من لوحة التحكم أولًا.")
        return

    df = data.copy()
    score_col = _score_column(df)

    # Normalize the fields used by the filters so missing scanner fields do not break the page.
    df[score_col] = _number(df, score_col)
    df["confirmation_score"] = _number(df, "confirmation_score")
    df["breakout_probability"] = _number(df, "breakout_probability")
    df["false_breakout_risk"] = _number(df, "false_breakout_risk", 100)
    df["relative_volume"] = _number(df, "relative_volume")
    df["momentum_score"] = _number(df, "momentum_score")
    df["liquidity_score"] = _number(df, "liquidity_score")

    if "symbol" not in df.columns:
        df["symbol"] = "—"
    if "phase" not in df.columns:
        df["phase"] = "غير محدد"
    df["symbol"] = df["symbol"].astype(str).str.upper()
    df["phase"] = df["phase"].fillna("غير محدد").astype(str)
    df["quality"] = df.apply(lambda row: _quality_label(row, score_col), axis=1)

    total = len(df)
    strong = int((df[score_col] >= 75).sum())
    breakout = int((df["breakout_probability"] >= 70).sum())
    liquidity = int((df["relative_volume"] >= 2).sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 الأسهم المكتشفة", total)
    m2.metric("🔥 فرص قوية", strong)
    m3.metric("🚀 اختراقات محتملة", breakout)
    m4.metric("💧 سيولة غير اعتيادية", liquidity)

    st.divider()
    st.subheader("🎯 فلترة ذكية")

    p1, p2, p3 = st.columns([1.2, 1.2, 1])
    preset = p1.selectbox(
        "نمط البحث",
        [
            "كل النتائج",
            "🔥 أفضل الفرص",
            "🚀 اختراقات محتملة",
            "💧 سيولة غير اعتيادية",
            "📈 زخم قوي",
            "🛡️ مخاطر أقل",
        ],
    )
    sort_by = p2.selectbox(
        "ترتيب النتائج",
        [
            "Opportunity Score",
            "Confidence",
            "Breakout Probability",
            "Relative Volume",
            "Momentum",
            "Liquidity",
            "False Breakout Risk",
        ],
    )
    direction = p3.radio("الاتجاه", ["الأعلى أولًا", "الأقل أولًا"], horizontal=True)

    f1, f2, f3, f4 = st.columns(4)
    min_score = f1.slider("🎯 الحد الأدنى للفرصة", 0, 100, 40, 5)
    min_rvol = f2.number_input("💧 أقل Relative Volume", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
    min_breakout = f3.slider("🚀 أقل احتمال اختراق", 0, 100, 0, 5)
    max_risk = f4.slider("🛡️ أقصى خطر اختراق كاذب", 0, 100, 100, 5)

    f5, f6 = st.columns([1, 2])
    phases = sorted(df["phase"].unique().tolist())
    phase = f5.selectbox("مرحلة الفرصة", ["الكل"] + phases)
    search = f6.text_input("🔍 ابحث عن رمز السهم", placeholder="مثال: NVDA أو AMD").strip().upper()

    view = _apply_preset(df, preset, score_col)
    view = view[view[score_col] >= min_score]
    view = view[view["relative_volume"] >= min_rvol]
    view = view[view["breakout_probability"] >= min_breakout]
    view = view[view["false_breakout_risk"] <= max_risk]

    if phase != "الكل":
        view = view[view["phase"] == phase]
    if search:
        view = view[view["symbol"].str.contains(search, na=False)]

    sort_map = {
        "Opportunity Score": score_col,
        "Confidence": "confirmation_score",
        "Breakout Probability": "breakout_probability",
        "Relative Volume": "relative_volume",
        "Momentum": "momentum_score",
        "Liquidity": "liquidity_score",
        "False Breakout Risk": "false_breakout_risk",
    }
    sort_col = sort_map[sort_by]
    view = view.sort_values(sort_col, ascending=direction == "الأقل أولًا", kind="stable")

    st.divider()
    h1, h2 = st.columns([3, 1])
    h1.subheader(f"🏆 النتائج المطابقة: {len(view)}")
    h2.download_button(
        "⬇️ تصدير CSV",
        data=view.to_csv(index=False).encode("utf-8-sig"),
        file_name="market_scan_results.csv",
        mime="text/csv",
        width="stretch",
    )

    if view.empty:
        st.warning("لم يتم العثور على فرص مطابقة للفلاتر الحالية. خفّض الحد الأدنى للفرصة أو وسّع الفلاتر.")
        return

    display_columns = [
        "symbol",
        "price",
        score_col,
        "confirmation_score",
        "breakout_probability",
        "false_breakout_risk",
        "relative_volume",
        "momentum_score",
        "liquidity_score",
        "phase",
        "quality",
    ]
    display_columns = [c for c in display_columns if c in view.columns]

    labels = {
        "symbol": "الرمز",
        "price": "السعر",
        score_col: "Opportunity Score",
        "confirmation_score": "Confidence",
        "breakout_probability": "Breakout %",
        "false_breakout_risk": "False Breakout %",
        "relative_volume": "RVOL",
        "momentum_score": "Momentum",
        "liquidity_score": "Liquidity",
        "phase": "المرحلة",
        "quality": "التصنيف",
    }

    table = view[display_columns].rename(columns=labels)
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "السعر": st.column_config.NumberColumn(format="$%.2f"),
            "Opportunity Score": st.column_config.ProgressColumn("Opportunity Score", min_value=0, max_value=100, format="%.1f"),
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%.1f"),
            "Breakout %": st.column_config.ProgressColumn("Breakout %", min_value=0, max_value=100, format="%.1f"),
            "False Breakout %": st.column_config.ProgressColumn("False Breakout %", min_value=0, max_value=100, format="%.1f"),
            "RVOL": st.column_config.NumberColumn(format="%.2fx"),
            "Momentum": st.column_config.NumberColumn(format="%.1f"),
            "Liquidity": st.column_config.NumberColumn(format="%.1f"),
        },
    )

    st.caption(
        "المصدر: نتائج آخر مسح محفوظة. فتح هذه الصفحة لا يبدأ مسحًا جديدًا ولا يرسل طلبات إضافية إلى Yahoo Finance."
    )
