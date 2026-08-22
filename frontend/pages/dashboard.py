"""AI Opportunity Engine dashboard — premium responsive financial terminal."""
from __future__ import annotations

import html

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
    return symbols, " + ".join(sources) if sources else "US Market Universe"


@st.cache_data(ttl=300, show_spinner=False)
def _load_yahoo_frames(symbols_tuple):
    return download_batches(symbols_tuple, period="6mo", interval="1d", batch_size=25, pause_seconds=1.5, max_retries=3)


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
        "scan_universe_source": st.session_state.get("scan_universe_source", "AI Opportunity Engine"),
        "market_regime": st.session_state.get("market_regime"),
    }


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _results(snapshot):
    data = snapshot.get("scan_results", pd.DataFrame())
    return data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame()


def render(auto_run=False):
    snapshot = _snapshot()
    last_scan = snapshot.get("last_scan_time") or "No scan yet"
    regime = snapshot.get("market_regime")
    regime_name = regime.get("regime", "READY") if isinstance(regime, dict) else "READY"
    universe, source = load_market_universe()

    topbar_html = (
        f'<div class="terminal-topbar">'
        f'<div class="terminal-market-pill"><span class="state-dot"></span><b>Scanner Ready</b></div>'
        f'<div><span>Universe</span><b>{len(universe):,}</b></div>'
        f'<div><span>Market Sample</span><b>{html.escape(str(regime_name))}</b></div>'
        f'<div class="topbar-last"><span>Last Scan</span><b>{html.escape(str(last_scan))}</b></div>'
        f'</div>'
        f'<div class="terminal-hero terminal-hero-v2">'
        f'<div><div class="terminal-eyebrow">AI OPPORTUNITY ENGINE</div>'
        f'<div class="terminal-title">🧠 AI Opportunity Engine</div>'
        f'<div class="terminal-sub">Advanced breakout, momentum and liquidity ranking across the current market universe.</div></div>'
        f'<div class="engine-state"><span class="state-dot"></span><b>Engine Online</b><small>AI-ranked opportunity workflow</small></div>'
        f'</div>'
    )
    st.markdown(topbar_html, unsafe_allow_html=True)

    config = st.session_state.get("sidebar_config", {})
    min_score = config.get("min_score", 40)
    max_symbols = config.get("max_symbols", 100)

    f1, f2, f3 = st.columns([2.15, .85, 1.0])
    with f1:
        st.markdown(f"<div class='terminal-filter-copy'>💡 Showing the strongest AI-ranked opportunities · Min score <b>{min_score}</b></div>", unsafe_allow_html=True)
    with f2:
        top_n = st.selectbox("Results", [5, 10, 15, 20], index=1, label_visibility="collapsed")
    with f3:
        run_here = st.button("🚀 Run Scanner", type="primary", width="stretch")

    if auto_run or run_here:
        _run_scan(universe, source, int(min_score), int(top_n), int(max_symbols))
        snapshot = _snapshot()

    display_metrics(snapshot)
    display_top_opportunities(snapshot)

    with st.expander("🌐 Engine details & activity", expanded=False):
        display_market_status(snapshot)
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
    candidate_limit = max(20, min(int(max_symbols), 40, len(symbols)))
    with st.spinner("🧠 محرك الفرص يجهز البيانات ويرتب المرشحين..."):
        frames = _load_yahoo_frames(tuple(symbols))
    if not frames:
        st.warning("تعذر الحصول على البيانات اللازمة في هذه الجولة.")
        return
    ranking = rank_discovery_candidates(frames, limit=candidate_limit)
    if ranking.empty:
        st.warning("لم يتم العثور على مرشحين صالحين.")
        return
    candidates = ranking["symbol"].tolist()
    scanner = BreakoutScanner()
    rows, errors, regime_frames = [], [], []
    progress = st.progress(0)
    status = st.empty()
    for index, symbol in enumerate(candidates, 1):
        status.caption(f"تحليل {symbol} · {index}/{len(candidates)}")
        frame = frames.get(symbol)
        try:
            result = scanner.scan_stock(symbol, df=frame)
            if not result or "error" in result:
                errors.append({"symbol": symbol, "error": (result or {}).get("error", "Unknown error")})
            else:
                indicators = result.get("indicators", {})
                rows.append({"symbol": symbol, "setup_score": result.get("score", 0), "breakout_probability": result.get("breakout_probability", 0), "false_breakout_risk": result.get("false_breakout_risk", 100), "liquidity_score": indicators.get("liquidity_score", indicators.get("volume_score", 0)), "momentum_score": indicators.get("momentum_score", indicators.get("breakout_score", 0)), "trend_score": float(indicators.get("trend_strength", 0)) * 100, "relative_volume": indicators.get("relative_volume", 1), "phase": result.get("phase", "WATCH"), "signal": result.get("signal", "WATCH"), "confirmation_score": result.get("confirmation_score", 0), "explanation": result.get("explanation", ""), "price": result.get("levels", {}).get("current", 0), "target": result.get("levels", {}).get("target_1", 0), "recommendation": result.get("recommendation", {}).get("action", "")})
                regime_frames.append(frame)
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)})
        progress.progress(index / len(candidates))
    progress.empty(); status.empty()
    ranked_all = rank_opportunities(rows, top_n=max(top_n, len(rows)))
    if ranked_all.empty:
        st.warning("لم يتم العثور على فرص قابلة للتحليل في هذه الجولة."); return
    ranked = ranked_all[ranked_all["setup_score"] >= min_score].head(top_n).reset_index(drop=True)
    if ranked.empty: ranked = ranked_all.head(top_n).reset_index(drop=True)
    regime = None
    if regime_frames:
        try: regime = detect_market_regime(pd.concat(regime_frames).sort_index())
        except Exception: pass
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = dict(scan_results=ranked, scan_results_all=ranked_all, scan_errors=pd.DataFrame(errors), scan_symbols_count=len(symbols), scan_success_count=len(rows), last_scan_time=now, scan_universe_source="AI Opportunity Engine", market_regime=regime)
    save_scan(**payload); st.session_state.update(payload)
    st.toast(f"اكتمل المسح: {len(rows)} سهم · {len(ranked)} فرصة", icon="✅")


def display_metrics(snapshot=None):
    snapshot = snapshot or _snapshot(); results = _results(snapshot)
    total = int(snapshot.get("scan_success_count", 0)); opportunities = len(results)
    avg = pd.to_numeric(results.get("opportunity_score", pd.Series(dtype=float)), errors="coerce").mean() if not results.empty else 0
    strong = int(results.get("signal_quality", pd.Series(dtype=str)).astype(str).str.contains("Strong|Elite|قوي|شراء", case=False, na=False).sum()) if not results.empty else 0
    cards = [("⚡", "Analyzed", f"{total}", "Stocks", "blue"), ("★", "Opportunities", f"{opportunities}", "Stocks", "violet"), ("◎", "Avg Opportunity Score", f"{float(avg or 0):.1f}", "/100", "green"), ("🔥", "Strong Opportunities", f"{strong}", "Stocks", "amber")]
    html_cards = "".join(f"<div class='terminal-stat-card'><div class='stat-icon {tone}'>{icon}</div><div><span>{label}</span><b>{value}</b><small>{suffix}</small></div></div>" for icon, label, value, suffix, tone in cards)
    st.markdown(f"<div class='terminal-stat-grid'>{html_cards}</div>", unsafe_allow_html=True)


def _bar(value, invert=False):
    value = max(0, min(100, _safe_float(value))); cls = "risk" if invert else "good"
    return f'<div class="mini-bar"><span class="{cls}" style="width:{value:.0f}%"></span></div>'


def _open_stock_analysis(symbol: str) -> None:
    """Navigate to stock analysis and remember the exact source page."""
    st.session_state.analysis_symbol = symbol
    st.session_state.analysis_return_page = st.session_state.get("active_page", "dashboard")
    st.session_state.active_page = "analysis"
    try: st.query_params.clear()
    except Exception: pass
    st.rerun()


def _cell(primary: str, secondary: str = "", css_class: str = "") -> str:
    secondary_html = f'<small class="{css_class}">{secondary}</small>' if secondary else ""
    return f'<div style="padding-top:6px"><b>{primary}</b>{secondary_html}</div>'


def display_top_opportunities(snapshot=None):
    results = _results(snapshot or _snapshot())
    st.markdown('<div class="section-head"><b>🔥 Top Opportunities</b><span>AI-ranked breakout candidates</span></div>', unsafe_allow_html=True)
    if results.empty:
        st.info("ستظهر أفضل الفرص هنا فور اكتمال أول مسح."); return
    widths = [0.35, 1.25, 1.0, 1.0, 1.15, 1.2, 1.1, 1.1, 0.85, 0.42]
    header = st.columns(widths, gap="small")
    labels = ["#", "Symbol", "Price", "Opportunity", "Breakout", "Relative Volume", "Momentum", "Liquidity", "Risk", ""]
    for col, label in zip(header, labels): col.markdown(f"<div style='font-size:.72rem;color:#8da0ba;font-weight:800;padding:4px 0 8px'>{label}</div>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(results.head(10).iterrows(), 1):
        raw_symbol = str(row.get("symbol", "—")).upper().strip(); symbol = html.escape(raw_symbol)
        price = _safe_float(row.get("price")); score = _safe_float(row.get("opportunity_score")); prob = _safe_float(row.get("breakout_probability")); rvol = _safe_float(row.get("relative_volume"), 1); momentum = _safe_float(row.get("momentum_score")); liquidity = _safe_float(row.get("liquidity_score")); risk = _safe_float(row.get("false_breakout_risk"))
        signal = html.escape(str(row.get("signal_class") or row.get("signal") or "WATCH")); risk_label = "LOW" if risk <= 25 else ("MEDIUM" if risk <= 40 else "HIGH"); risk_class = "low" if risk <= 25 else ("medium" if risk <= 40 else "high"); volume_label = "High" if rvol >= 1.5 else "Average"
        with st.container(border=True):
            cols = st.columns(widths, gap="small", vertical_alignment="center")
            cols[0].markdown(f"<div style='color:#73869f;text-align:center'>{i}</div>", unsafe_allow_html=True); cols[1].markdown(_cell(symbol, signal), unsafe_allow_html=True); cols[2].markdown(_cell(f"${price:,.2f}"), unsafe_allow_html=True); cols[3].markdown(f'<div style="padding-top:2px"><span class="score-ring">{score:.1f}</span></div>', unsafe_allow_html=True); cols[4].markdown(_cell(f"{prob:.0f}%") + _bar(prob), unsafe_allow_html=True); cols[5].markdown(_cell(f"{rvol:.2f}x", volume_label, "positive"), unsafe_allow_html=True); cols[6].markdown(_cell(f"{momentum:.0f}/100") + _bar(momentum), unsafe_allow_html=True); cols[7].markdown(_cell(f"{liquidity:.0f}/100") + _bar(liquidity), unsafe_allow_html=True); cols[8].markdown(_cell(f"{risk:.0f}%", risk_label, risk_class), unsafe_allow_html=True)
            if cols[9].button("↗", key=f"view_stock_{raw_symbol}_{i}", help=f"استعراض وتحليل {raw_symbol}", width="stretch"): _open_stock_analysis(raw_symbol)


def display_market_status(snapshot=None):
    snapshot = snapshot or _snapshot(); errors = snapshot.get("scan_errors", pd.DataFrame()); regime = snapshot.get("market_regime"); regime_name = regime.get("regime", "READY") if isinstance(regime, dict) else "READY"
    c1, c2, c3 = st.columns(3); c1.metric("Engine", "AI Opportunity Engine"); c2.metric("Market Sample", regime_name); c3.metric("Errors", len(errors) if isinstance(errors, pd.DataFrame) else 0)
    if snapshot.get("last_scan_time"): st.caption(f"آخر مسح: {snapshot['last_scan_time']}")


def display_activity(snapshot=None):
    results = _results(snapshot or _snapshot())
    if results.empty: return
    c1, c2 = st.columns(2)
    if "relative_volume" in results.columns:
        chart = results[["symbol", "relative_volume"]].copy(); chart["relative_volume"] = pd.to_numeric(chart["relative_volume"], errors="coerce"); chart = chart.dropna().sort_values("relative_volume", ascending=False).head(10)
        if not chart.empty:
            with c1: st.plotly_chart(px.bar(chart, x="symbol", y="relative_volume", title="Relative Volume"), width="stretch")
    if "opportunity_score" in results.columns:
        chart = results[["symbol", "opportunity_score"]].copy(); chart["opportunity_score"] = pd.to_numeric(chart["opportunity_score"], errors="coerce"); chart = chart.dropna().sort_values("opportunity_score", ascending=False).head(10)
        if not chart.empty:
            with c2:
                fig = px.bar(chart, x="symbol", y="opportunity_score", title="Opportunity Score"); fig.update_layout(yaxis_range=[0, 100]); st.plotly_chart(fig, width="stretch")


def display_charts(): display_activity()
def display_scan_results(): display_top_opportunities()
