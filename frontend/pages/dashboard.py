"""لوحة واحدة: اكتشاف السوق + المسح + أفضل الفرص."""

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.results_store import get_scan, save_scan
from backend.data.yahoo_universe import DEFAULT_UNIVERSE, download_batches, rank_discovery_candidates

DEFAULT_SYMBOLS = list(DEFAULT_UNIVERSE)


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_universe():
    symbols, sources = [], []
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
    return symbols, " + ".join(sources) if sources else "القائمة الافتراضية الموسعة"


@st.cache_data(ttl=300, show_spinner=False)
def _load_yahoo_frames(symbols_tuple):
    return download_batches(
        symbols_tuple,
        period="6mo",
        interval="1d",
        batch_size=40,
        pause_seconds=1.0,
        max_retries=2,
    )


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
    st.caption("اكتشاف فرص الاختراق والزخم والسيولة من شاشة واحدة — النظام يبحث عن الأسهم تلقائيًا ثم يحلل الأفضل.")

    config = st.session_state.get("sidebar_config", {})
    min_score = config.get("min_score", 40)
    max_symbols = config.get("max_symbols", 100)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.info("🤖 المسح الذكي: جلب دفعات من Yahoo، فلترة سريعة، ثم تحليل عميق لأقوى المرشحين.")
    with c2:
        top_n = st.number_input("أفضل النتائج", min_value=5, max_value=20, value=10, step=1)
    with c3:
        run_here = st.button("🚀 تشغيل المسح", type="primary", width="stretch")

    universe, source = load_market_universe()
    st.caption(f"📡 {source} — قاعدة الاكتشاف تحتوي {len(universe)} سهمًا.")

    if auto_run or run_here:
        _run_scan(universe, source, int(min_score), int(top_n), int(max_symbols))

    snapshot = _snapshot()
    display_metrics(snapshot)
    st.markdown("---")
    display_market_status(snapshot)
    st.markdown("---")
    display_top_opportunities(snapshot)
    st.markdown("---")
    display_activity(snapshot)


def _run_scan(symbols, source, min_score, top_n, max_symbols):
    try:
        from backend.scanner.breakout_scanner import BreakoutScanner
        from backend.ranking.opportunity_ranker import rank_opportunities
        from backend.market.regime import detect_market_regime
    except Exception as exc:
        st.error(f"تعذر تحميل محرك المسح: {exc}")
        return
    if not symbols:
        st.warning("لم يتم اكتشاف أسهم للمسح.")
        return

    # نضع سقفًا للمرحلة العميقة حتى لا نضغط Yahoo بطلبات إضافية.
    candidate_limit = max(20, min(int(max_symbols), 40, len(symbols)))
    normalized = tuple(symbols)

    with st.spinner(f"📡 يجلب النظام بيانات السوق على دفعات آمنة من Yahoo Finance..."):
        frames = _load_yahoo_frames(normalized)

    if not frames:
        st.warning("تعذر الحصول على بيانات Yahoo في هذه الجولة. سيتم الاحتفاظ بالنتائج السابقة إن وجدت.")
        return

    ranking = rank_discovery_candidates(frames, limit=candidate_limit)
    if ranking.empty:
        st.warning("لم يتم العثور على مرشحين صالحين من البيانات المتاحة.")
        return

    candidates = ranking["symbol"].tolist()
    st.success(f"🔎 اكتشف النظام {len(candidates)} مرشحًا من {len(symbols)} سهمًا، دون طلب منفصل لكل سهم.")

    scanner = BreakoutScanner()
    rows, errors, regime_frames = [], [], []
    progress = st.progress(0)
    status = st.empty()

    for index, symbol in enumerate(candidates, 1):
        status.caption(f"🤖 تحليل عميق {symbol} ({index}/{len(candidates)})")
        frame = frames.get(symbol)
        try:
            # نمرر البيانات التي جلبناها بالفعل؛ لا يعيد Scanner طلب Yahoo.
            result = scanner.scan_stock(symbol, df=frame)
            if not result or "error" in result:
                errors.append({"symbol": symbol, "error": (result or {}).get("error", "Unknown error")})
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
                    "signal": result.get("signal", "👀 WATCH"),
                    "confirmation_score": result.get("confirmation_score", 0),
                    "explanation": result.get("explanation", ""),
                    "price": result.get("levels", {}).get("current", 0),
                    "target": result.get("levels", {}).get("target_1", 0),
                    "recommendation": result.get("recommendation", {}).get("action", ""),
                })
                regime_frames.append(frame)
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)})
        progress.progress(index / len(candidates))

    progress.empty()
    status.empty()

    ranked_all = rank_opportunities(rows, top_n=max(top_n, len(rows)))
    if ranked_all.empty:
        st.warning("لم يتم العثور على فرص قابلة للتحليل في هذه الجولة.")
        return

    ranked = ranked_all[ranked_all["setup_score"] >= min_score].head(top_n).reset_index(drop=True)
    if ranked.empty:
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
    discovery_source = f"{source} → Yahoo Batch Discovery {len(symbols)} → Deep Analysis {len(candidates)}"
    save_scan(
        scan_results=ranked,
        scan_results_all=ranked_all,
        scan_errors=errors_df,
        scan_symbols_count=len(symbols),
        scan_success_count=len(rows),
        last_scan_time=now,
        scan_universe_source=discovery_source,
        market_regime=regime,
    )
    st.session_state.update({
        "scan_results": ranked.copy(),
        "scan_results_all": ranked_all.copy(),
        "scan_errors": errors_df,
        "scan_symbols_count": len(symbols),
        "scan_success_count": len(rows),
        "last_scan_time": now,
        "scan_universe_source": discovery_source,
        "market_regime": regime,
    })
    st.success(f"✅ اكتمل المسح الذكي: تم تحليل {len(rows)} مرشحًا وعرض أفضل {len(ranked)} فرص.")


def _results(snapshot):
    data = snapshot.get("scan_results", pd.DataFrame())
    return data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame()


def display_metrics(snapshot=None):
    snapshot = snapshot or _snapshot()
    results = _results(snapshot)
    total = int(snapshot.get("scan_success_count", 0))
    opportunities = len(results)
    avg = pd.to_numeric(results.get("opportunity_score", pd.Series(dtype=float)), errors="coerce").mean() if not results.empty else 0
    strong = int(results.get("signal_quality", pd.Series(dtype=str)).astype(str).str.contains("Strong|Elite|قوي|شراء", case=False, na=False).sum()) if not results.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 أسهم تم تحليلها", total)
    c2.metric("🔥 أفضل الفرص", opportunities)
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
        st.info("🔎 لم يتم تنفيذ مسح بعد. استخدم زر المسح لبدء الاكتشاف التلقائي.")


def _fmt(value, suffix="", decimals=1):
    try:
        return f"{float(value):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "—"


def display_top_opportunities(snapshot=None):
    results = _results(snapshot or _snapshot())
    st.subheader("🔥 أفضل الفرص الآن")
    if results.empty:
        st.info("ستظهر الأسهم هنا فور اكتمال أول مسح.")
        return
    preferred = ["rank", "symbol", "price", "opportunity_score", "signal_class", "signal_quality", "signal", "confirmation_score", "breakout_probability", "false_breakout_risk", "relative_volume", "phase", "recommendation"]
    cols = [c for c in preferred if c in results.columns]
    display = results[cols].head(10).copy()
    display = display.rename(columns={
        "rank": "#", "symbol": "السهم", "price": "السعر", "opportunity_score": "الفرصة",
        "signal_class": "التصنيف", "signal_quality": "الجودة", "signal": "الإشارة", "confirmation_score": "التأكيد",
        "breakout_probability": "احتمال الاختراق", "false_breakout_risk": "خطر الاختراق الكاذب", "relative_volume": "Relative Volume",
        "phase": "المرحلة", "recommendation": "التوصية",
    })
    st.dataframe(display, width="stretch", hide_index=True, height=min(500, 110 + len(display) * 38))
    st.subheader("🎯 لماذا ظهرت هذه الأسهم؟")
    for _, row in results.head(5).iterrows():
        symbol = row.get("symbol", "-")
        score = float(row.get("opportunity_score", 0))
        with st.expander(f"{row.get('signal', '👀 WATCH')}  {symbol} — Opportunity Score {score:.1f}"):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("السعر", f"${float(row.get('price', 0)):.2f}")
            c2.metric("التأكيد", _fmt(row.get("confirmation_score", 0), "/100"))
            c3.metric("AI / الاختراق", _fmt(row.get("breakout_probability", 0), "%"))
            c4.metric("الخطر", _fmt(row.get("false_breakout_risk", 0), "%"))
            c5.metric("Relative Volume", _fmt(row.get("relative_volume", 1), "x", 2))
            st.markdown(f"**المرحلة:** `{row.get('phase', 'WATCH')}`")
            if row.get("explanation", ""):
                st.info(f"💡 {row.get('explanation')}")
            if row.get("recommendation", ""):
                st.markdown(f"**التوصية:** {row.get('recommendation')}" )


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
