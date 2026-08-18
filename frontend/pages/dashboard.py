"""لوحة واحدة: حالة السوق + إعدادات المسح + النتائج."""

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.results_store import get_scan, save_scan

DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "AMD", "AMZN", "META", "GOOGL", "TSLA",
    "PLTR", "AVGO", "NFLX", "CRM", "ORCL", "COIN", "SMCI",
]


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_universe():
    symbols = []
    sources = []
    try:
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        if "Symbol" in sp500.columns:
            symbols.extend(sp500["Symbol"].astype(str).str.replace(".", "-", regex=False).tolist())
            sources.append(f"S&P 500: {len(sp500)}")
    except Exception:
        pass
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        nasdaq = next((t for t in tables if "Ticker" in t.columns), None)
        if nasdaq is not None:
            symbols.extend(nasdaq["Ticker"].astype(str).tolist())
            sources.append(f"Nasdaq-100: {len(nasdaq)}")
    except Exception:
        pass
    symbols.extend(DEFAULT_SYMBOLS)
    symbols = list(dict.fromkeys(s.strip().upper() for s in symbols if s and s.strip()))
    return symbols, " + ".join(sources) if sources else "القائمة الافتراضية"


def _snapshot():
    shared = get_scan()
    if shared.get("last_scan_time"):
        return shared
    return {
        "scan_results": st.session_state.get("scan_results", pd.DataFrame()),
        "scan_results_all": st.session_state.get("scan_results_all", pd.DataFrame()),
        "scan_errors": st.session_state.get("scan_errors", pd.DataFrame()),
        "scan_symbols_count": st.session_state.get("scan_symbols_count", 0),
        "scan_success_count": st.session_state.get("scan_success_count", 0),
        "last_scan_time": st.session_state.get("last_scan_time"),
        "scan_universe_source": st.session_state.get("scan_universe_source", "لم يتم إجراء مسح بعد"),
        "market_regime": st.session_state.get("market_regime"),
    }


def render(auto_run=False):
    st.title("🚀 AI Breakout Scanner")
    st.caption("اكتشاف فرص الاختراق والزخم والسيولة من شاشة واحدة — بدون التنقل بين صفحات.")

    config = st.session_state.get("sidebar_config", {})
    min_score = config.get("min_score", 40)
    max_symbols = config.get("max_symbols", 50)

    # The dashboard owns the scan controls. The sidebar button only requests a run.
    control1, control2, control3 = st.columns([2, 1, 1])
    with control1:
        scan_mode = st.radio(
            "مصدر الأسهم",
            ["🔎 مسح تلقائي للسوق", "✍️ أسهم محددة"],
            horizontal=True,
            label_visibility="collapsed",
        )
    with control2:
        top_n = st.number_input("أفضل النتائج", min_value=5, max_value=20, value=10, step=1)
    with control3:
        run_here = st.button("🚀 تشغيل المسح", type="primary", width="stretch")

    if scan_mode == "🔎 مسح تلقائي للسوق":
        universe, source = load_market_universe()
        count = min(max_symbols, len(universe))
        symbols = universe[:count]
        st.caption(f"📡 {source} — سيتم فحص {len(symbols)} سهمًا تلقائيًا.")
    else:
        source = "أسهم محددة"
        text = st.text_input("الأسهم المراد فحصها", value=", ".join(DEFAULT_SYMBOLS))
        symbols = list(dict.fromkeys(x.strip().upper() for x in text.split(",") if x.strip()))
        symbols = symbols[:max_symbols]
        st.caption(f"سيتم فحص {len(symbols)} سهمًا.")

    if auto_run or run_here:
        _run_scan(symbols, source, int(min_score), int(top_n))

    snapshot = _snapshot()
    display_metrics(snapshot)
    st.markdown("---")
    display_market_status(snapshot)
    st.markdown("---")
    display_top_opportunities(snapshot)
    st.markdown("---")
    display_activity(snapshot)


def _run_scan(symbols, source, min_score, top_n):
    # Lazy imports prevent the dashboard from failing before a scan is requested.
    try:
        import yfinance as yf
        from backend.scanner.breakout_scanner import BreakoutScanner
        from backend.ranking.opportunity_ranker import rank_opportunities
        from backend.market.regime import detect_market_regime
    except Exception as exc:
        st.error(f"تعذر تحميل محرك المسح: {exc}")
        return

    if not symbols:
        st.warning("لم يتم تحديد أسهم للمسح.")
        return

    scanner = BreakoutScanner()
    rows, errors, regime_frames = [], [], []
    progress = st.progress(0)
    status = st.empty()

    for index, symbol in enumerate(symbols):
        status.caption(f"🔎 تحليل {symbol} ({index + 1}/{len(symbols)})")
        try:
            result = scanner.scan_stock(symbol)
        except Exception as exc:
            result = {"error": str(exc)}

        if "error" in result:
            errors.append({"symbol": symbol, "error": result["error"]})
        else:
            indicators = result.get("indicators", {})
            rows.append({
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
            })
            try:
                frame = yf.Ticker(symbol).history(period="3mo", auto_adjust=False)
                if not frame.empty:
                    regime_frames.append(frame)
            except Exception:
                pass
        progress.progress((index + 1) / len(symbols))

    progress.empty()
    status.empty()

    ranked_all = rank_opportunities(rows, top_n=max(top_n, len(rows)))
    ranked = ranked_all[ranked_all["setup_score"] >= min_score].head(top_n).reset_index(drop=True) if not ranked_all.empty else ranked_all
    if ranked.empty and not ranked_all.empty:
        ranked = ranked_all.head(top_n).reset_index(drop=True)
        st.warning(f"لا توجد فرص بدرجة إعداد ≥ {min_score}. نعرض أفضل المرشحين بدل ترك الصفحة فارغة.")

    regime = None
    if regime_frames:
        try:
            regime = detect_market_regime(pd.concat(regime_frames).sort_index())
        except Exception:
            regime = None

    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    errors_df = pd.DataFrame(errors)
    save_scan(
        scan_results=ranked,
        scan_results_all=ranked_all,
        scan_errors=errors_df,
        scan_symbols_count=len(symbols),
        scan_success_count=len(rows),
        last_scan_time=now,
        scan_universe_source=source,
        market_regime=regime,
    )
    st.session_state.update({
        "scan_results": ranked.copy(),
        "scan_results_all": ranked_all.copy(),
        "scan_errors": errors_df,
        "scan_symbols_count": len(symbols),
        "scan_success_count": len(rows),
        "last_scan_time": now,
        "scan_universe_source": source,
        "market_regime": regime,
    })
    st.success(f"✅ اكتمل المسح: تم تحليل {len(rows)} من {len(symbols)} سهمًا — {len(ranked)} فرصة معروضة.")


def _results(snapshot):
    data = snapshot.get("scan_results", pd.DataFrame())
    return data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame()


def display_metrics(snapshot=None):
    snapshot = snapshot or _snapshot()
    results = _results(snapshot)
    total = int(snapshot.get("scan_success_count", 0))
    opportunities = len(results)
    avg = pd.to_numeric(results.get("opportunity_score", pd.Series(dtype=float)), errors="coerce").mean() if not results.empty else 0
    strong = int(results.get("signal_quality", pd.Series(dtype=str)).astype(str).str.contains("STRONG|قوي|BUY|شراء", case=False, na=False).sum()) if not results.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 أسهم تم تحليلها", total)
    c2.metric("🔥 فرص مكتشفة", opportunities)
    c3.metric("⭐ متوسط درجة الفرصة", f"{float(avg or 0):.1f}%")
    c4.metric("🚀 إشارات قوية", strong)


def display_market_status(snapshot=None):
    snapshot = snapshot or _snapshot()
    st.subheader("🌐 حالة السوق")
    regime = snapshot.get("market_regime")
    errors = snapshot.get("scan_errors", pd.DataFrame())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("المصدر", snapshot.get("scan_universe_source", "لم يتم إجراء مسح بعد"))
    c2.metric("حالة السوق", regime.get("regime", "غير متاح") if isinstance(regime, dict) else "غير متاح")
    c3.metric("تم تحليلها", snapshot.get("scan_success_count", 0))
    c4.metric("تعذر تحليلها", len(errors) if isinstance(errors, pd.DataFrame) else 0)
    if snapshot.get("last_scan_time"):
        st.caption(f"آخر مسح: {snapshot['last_scan_time']}")
    else:
        st.info("🔎 لم يتم تنفيذ مسح بعد. استخدم زر المسح من اليمين أو القائمة الجانبية.")


def display_top_opportunities(snapshot=None):
    results = _results(snapshot or _snapshot())
    st.subheader("🔥 أفضل الفرص الآن")
    if results.empty:
        st.info("ستظهر الأسهم هنا فور اكتمال أول مسح.")
        return
    preferred = ["rank", "symbol", "price", "opportunity_score", "signal_quality", "breakout_probability", "false_breakout_risk", "relative_volume", "phase", "recommendation"]
    cols = [c for c in preferred if c in results.columns]
    display = results[cols].head(10).copy()
    display = display.rename(columns={
        "rank": "#", "symbol": "السهم", "price": "السعر", "opportunity_score": "الفرصة",
        "signal_quality": "الجودة", "breakout_probability": "احتمال الاختراق",
        "false_breakout_risk": "خطر الاختراق الكاذب", "relative_volume": "Relative Volume",
        "phase": "المرحلة", "recommendation": "الإشارة",
    })
    st.dataframe(display, width="stretch", hide_index=True, height=min(430, 100 + len(display) * 35))

    st.subheader("🔎 تفاصيل سريعة")
    for _, row in results.head(5).iterrows():
        symbol = row.get("symbol", "-")
        score = float(row.get("opportunity_score", 0))
        with st.expander(f"🔥 {symbol} — Opportunity Score {score:.1f}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("السعر", f"${float(row.get('price', 0)):.2f}")
            c2.metric("احتمال الاختراق", f"{float(row.get('breakout_probability', 0)):.1f}%")
            c3.metric("الخطر", f"{float(row.get('false_breakout_risk', 0)):.1f}%")
            c4.metric("Relative Volume", f"{float(row.get('relative_volume', 1)):.2f}x")


def display_activity(snapshot=None):
    results = _results(snapshot or _snapshot())
    st.subheader("⚡ نشاط الفرص والسيولة")
    if results.empty:
        st.info("سيظهر النشاط بعد أول مسح للسوق.")
        return
    c1, c2 = st.columns(2)
    if "relative_volume" in results.columns:
        chart = results[["symbol", "relative_volume"]].copy()
        chart["relative_volume"] = pd.to_numeric(chart["relative_volume"], errors="coerce")
        chart = chart.dropna().sort_values("relative_volume", ascending=False).head(10)
        if not chart.empty:
            with c1:
                st.plotly_chart(px.bar(chart, x="symbol", y="relative_volume", title="أعلى Relative Volume"), width="stretch")
    if "opportunity_score" in results.columns:
        chart = results[["symbol", "opportunity_score"]].copy()
        chart["opportunity_score"] = pd.to_numeric(chart["opportunity_score"], errors="coerce")
        chart = chart.dropna().sort_values("opportunity_score", ascending=False).head(10)
        if not chart.empty:
            with c2:
                fig = px.bar(chart, x="symbol", y="opportunity_score", title="أعلى Opportunity Score")
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, width="stretch")


def display_charts():
    display_activity()


def display_scan_results():
    display_top_opportunities()
