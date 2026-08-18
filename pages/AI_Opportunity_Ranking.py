import streamlit as st
import pandas as pd
import yfinance as yf

from backend.scanner.breakout_scanner import BreakoutScanner
from backend.ranking.opportunity_ranker import rank_opportunities
from backend.ranking.explanations import explain_opportunity
from backend.market.regime import detect_market_regime


st.set_page_config(page_title="AI Opportunity Ranking", page_icon="🏆", layout="wide")

st.title("🏆 AI Opportunity Ranking")
st.caption("ترتيب الفرص يجمع الاختراق والسيولة والزخم والاتجاه ومخاطر الاختراق الكاذب.")

DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "AMD", "AMZN", "META", "GOOGL", "TSLA",
    "PLTR", "AVGO", "NFLX", "CRM", "ORCL", "COIN", "SMCI"
]

symbols_text = st.text_input("الأسهم المراد فحصها", value=", ".join(DEFAULT_SYMBOLS))
min_score = st.slider("الحد الأدنى لدرجة الإعداد", 0, 100, 50)
top_n = st.slider("عدد أفضل الفرص", 5, 20, 10)

if st.button("🚀 تشغيل الفحص", type="primary", use_container_width=True):
    symbols = [s.strip().upper() for s in symbols_text.split(",") if s.strip()]
    scanner = BreakoutScanner()
    rows = []
    regime_frames = []
    progress = st.progress(0)

    for index, symbol in enumerate(dict.fromkeys(symbols)):
        result = scanner.scan_stock(symbol)
        if "error" in result:
            continue
        indicators = result.get("indicators", {})
        row = {
            "symbol": symbol,
            "setup_score": result.get("score", 0),
            "breakout_probability": result.get("breakout_probability", 0),
            "false_breakout_risk": result.get("false_breakout_risk", 100),
            "liquidity_score": indicators.get("liquidity_score", indicators.get("volume_score", 0)),
            "momentum_score": indicators.get("momentum_score", indicators.get("breakout_score", 0)),
            "trend_score": float(indicators.get("trend_strength", 0)) * 100,
            "relative_volume": indicators.get("relative_volume", 1),
            "phase": result.get("phase", "WATCH"),
            "price": result.get("levels", {}).get("current", 0),
            "target": result.get("levels", {}).get("target_1", 0),
            "recommendation": result.get("recommendation", {}).get("action", ""),
        }
        rows.append(row)
        try:
            regime_df = yf.Ticker(symbol).history(period="3mo", auto_adjust=False)
            if not regime_df.empty:
                regime_frames.append(regime_df)
        except Exception:
            pass
        progress.progress((index + 1) / max(len(symbols), 1))

    progress.empty()
    ranked = rank_opportunities(rows, top_n=top_n)
    ranked = ranked[ranked["setup_score"] >= min_score].reset_index(drop=True)

    if regime_frames:
        market_df = pd.concat(regime_frames).sort_index()
        regime = detect_market_regime(market_df)
        c1, c2, c3 = st.columns(3)
        c1.metric("حالة السوق", regime["regime"])
        c2.metric("Trend Score", f"{regime['trend_score']:.1f}")
        c3.metric("Volatility", f"{regime['volatility_score']:.1f}")

    if ranked.empty:
        st.warning("لم يتم العثور على فرص مطابقة للشروط الحالية.")
    else:
        st.subheader("أفضل الفرص")
        display = ranked[[
            "rank", "symbol", "opportunity_score", "signal_quality",
            "breakout_probability", "false_breakout_risk", "phase", "price", "target"
        ]].copy()
        display.columns = [
            "الترتيب", "السهم", "الفرصة", "الجودة", "احتمال الاختراق",
            "خطر الاختراق الكاذب", "المرحلة", "السعر", "الهدف"
        ]
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.subheader("لماذا هذه الأسهم؟")
        for _, row in ranked.iterrows():
            with st.expander(f"#{int(row['rank'])} {row['symbol']} — {row['opportunity_score']:.1f} ({row['signal_quality']})"):
                reasons = explain_opportunity(row.to_dict())
                for reason in reasons:
                    st.write(f"✓ {reason}")
                st.write(f"**المرحلة:** {row['phase']}")
                st.write(f"**احتمال الاختراق:** {row['breakout_probability']:.1f}%")
                st.write(f"**مخاطر الاختراق الكاذب:** {row['false_breakout_risk']:.1f}%")
                st.write(f"**السعر:** ${row['price']:.2f} | **الهدف الأول:** ${row['target']:.2f}")
else:
    st.info("اختر الأسهم ثم اضغط تشغيل الفحص لعرض أفضل فرص الاختراق.")
