"""
صفحة بيانات السوق الأمريكية - جلب وعرض الأسهم والمؤشرات والصناديق
"""

from datetime import datetime, timedelta
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ============================================================================
# البيانات الأساسية
# ============================================================================

US_INDICES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "NASDAQ",
    "^RUT": "Russell 2000",
    "^VIX": "VIX - التقلبات",
    "^FTSE": "FTSE 100",
    "^N225": "Nikkei 225",
    "^HSI": "Hang Seng",
}

POPULAR_ETFS = {
    "SPY": "S&P 500 ETF",
    "QQQ": "NASDAQ 100 ETF",
    "DIA": "Dow Jones ETF",
    "IWM": "Russell 2000 ETF",
    "VTI": "Total Stock Market",
    "VOO": "S&P 500 Vanguard",
    "BND": "Total Bond Market",
    "GLD": "Gold ETF",
    "SLV": "Silver ETF",
    "USO": "Oil ETF",
    "TQQQ": "NASDAQ 3x Bull",
    "SQQQ": "NASDAQ 3x Bear",
}

POPULAR_STOCKS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms",
    "TSLA": "Tesla Inc.",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel Corp.",
    "NFLX": "Netflix Inc.",
    "PYPL": "PayPal Holdings",
    "ADBE": "Adobe Inc.",
    "CRM": "Salesforce Inc.",
    "ORCL": "Oracle Corp.",
    "IBM": "IBM Corp.",
    "CSCO": "Cisco Systems",
    "QCOM": "Qualcomm Inc.",
    "TXN": "Texas Instruments",
    "AVGO": "Broadcom Inc.",
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "WFC": "Wells Fargo",
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PFE": "Pfizer Inc.",
    "WMT": "Walmart Inc.",
    "PG": "Procter & Gamble",
    "KO": "Coca-Cola Co.",
    "XOM": "Exxon Mobil",
    "CVX": "Chevron Corp.",
}


# ============================================================================
# 1. تطبيق التنسيقات المتدرجة (Gradients & Custom CSS)
# ============================================================================
def apply_custom_styles():
    st.markdown(
        """
    <style>
    /* 1. التنسيق العام للتطبيق */
    .stApp {
        background-color: #0F172A;
        color: #FFFFFF;
    }
    
    /* 2. إصلاح مربعات الإدخال والقوائم المنسدلة (تغميق الخلفية وإظهار النص) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    input {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    /* 3. إصلاح نص الإدخال والعناصر داخل المربعات */
    input::placeholder {
        color: #9CA3AF !important;
    }
    
    div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* 4. إصلاح خيارات القائمة المنسدلة (Dropdown Menu) */
    ul[role="listbox"], 
    div[data-baseweb="popover"] div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    /* 5. بطاقات التنسيق المتدرج */
    .gradient-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .gradient-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.5);
    }

    .card-purple { background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%); border-color: rgba(168, 85, 247, 0.4); }
    .card-green { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%); border-color: rgba(16, 185, 129, 0.4); }
    .card-gold { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%); border-color: rgba(245, 158, 11, 0.4); }

    .card-title { color: #9CA3AF !important; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; }
    .card-value { color: #FFFFFF !important; font-size: 1.6rem; font-weight: 800; }
    .card-sub { font-size: 0.8rem; font-weight: 700; margin-top: 4px; display: inline-block; padding: 2px 8px; border-radius: 12px; }
    
    .sub-green { background: rgba(16, 185, 129, 0.25); color: #10B981 !important; }
    .sub-gold { background: rgba(245, 158, 11, 0.25); color: #F59E0B !important; }
    .sub-purple { background: rgba(168, 85, 247, 0.25); color: #C084FC !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ============================================================================
# دوال جلب البيانات
# ============================================================================


@st.cache_data(ttl=60)
def fetch_stock_data(symbol, period="1d", interval="1d"):
    """تعديل الفاصل الزمني الافتراضي إلى 1d ليتناسب مع الفترات الطويلة"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except:
        return {}


@st.cache_data(ttl=60)
def fetch_multiple_stocks(symbols):
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")

            if not history.empty:
                current_price = history["Close"].iloc[-1]
                previous_close = info.get("previousClose", current_price)
                change = current_price - previous_close
                change_percent = (
                    (change / previous_close) * 100 if previous_close > 0 else 0
                )
            else:
                current_price = 0
                change = 0
                change_percent = 0

            data[symbol] = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "غير معروف"),
                "price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend": info.get("dividendRate", 0),
                "high_52": info.get("fiftyTwoWeekHigh", 0),
                "low_52": info.get("fiftyTwoWeekLow", 0),
            }
        except:
            continue

    return pd.DataFrame(data).T


# ============================================================================
# عرض الأسهم والمؤشرات والتصنيفات
# ============================================================================


def render():
    """عرض صفحة بيانات السوق"""
    apply_custom_styles()  # 👈 تم إضافة استدعاء التنسيقات هنا لضمان عملها

    st.subheader("📊 بيانات السوق الأمريكية")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 الأسهم", "📊 المؤشرات", "🏦 الصناديق", "🔍 بحث شامل"]
    )

    with tab1:
        render_stocks()

    with tab2:
        render_indices()

    with tab3:
        render_etfs()

    with tab4:
        render_search()


def render_market_data():
    render()


def render_stocks():
    st.markdown("### 📈 الأسهم الأمريكية")
    sectors = [
        "الكل",
        "التكنولوجيا",
        "المالية",
        "الرعاية الصحية",
        "الاستهلاك",
        "الطاقة",
        "الصناعة",
    ]
    selected_sector = st.selectbox(
        "تصفية حسب القطاع:", sectors, key="stock_sector"
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        max_stocks = st.number_input(
            "عدد الأسهم:",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            key="stock_count",
        )

    with st.spinner("جاري جلب بيانات الأسهم..."):
        stocks_to_fetch = list(POPULAR_STOCKS.keys())[:max_stocks]
        df = fetch_multiple_stocks(stocks_to_fetch)

        if df.empty:
            st.warning("⚠️ لا توجد بيانات متاحة حالياً")
            return

        if selected_sector != "الكل":
            df = df[df["sector"] == selected_sector]

        display_stock_table(df)

    st.markdown("---")
    st.markdown("### 🔍 تحليل سهم محدد")

    selected_symbol = st.selectbox(
        "اختر سهماً للتحليل:",
        list(POPULAR_STOCKS.keys()),
        key="stock_select_analysis",
    )

    if selected_symbol:
        display_stock_analysis(selected_symbol)


def display_stock_table(df):
    if df.empty:
        st.info("لا توجد أسهم في هذا القطاع")
        return

    display_df = df.copy()
    display_df["price"] = display_df["price"].apply(
        lambda x: f"${x:.2f}" if isinstance(x, (int, float)) and x > 0 else "N/A"
    )
    display_df["change"] = display_df["change"].apply(
        lambda x: f"${x:.2f}"
        if isinstance(x, (int, float)) and x != 0
        else "$0.00"
    )
    display_df["change_percent"] = display_df["change_percent"].apply(
        lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else "0.00%"
    )

    st.dataframe(
        display_df[
            [
                "symbol",
                "name",
                "sector",
                "price",
                "change",
                "change_percent",
                "volume",
            ]
        ],
        column_config={
            "symbol": "الرمز",
            "name": "الشركة",
            "sector": "القطاع",
            "price": "السعر",
            "change": "التغير",
            "change_percent": "التغير %",
            "volume": "حجم التداول",
        },
        use_container_width=True,
        hide_index=True,
    )


def display_stock_analysis(symbol):
    with st.spinner(f"جاري تحليل {symbol}..."):
        info = fetch_stock_info(symbol)
        # تم تحديد interval='1d' لتفادي خطأ الفترات الطويلة مع '1m'
        df = fetch_stock_data(symbol, period="3mo", interval="1d")

        if df.empty:
            st.error(f"❌ لا توجد بيانات بالسهم {symbol}")
            return

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            current_price = df["Close"].iloc[-1]
            st.metric("💰 السعر", f"${current_price:.2f}")
        with col2:
            prev = info.get("previousClose", current_price)
            diff = current_price - prev
            pct = (diff / prev) * 100 if prev > 0 else 0
            st.metric("📊 التغير", f"${diff:.2f}", delta=f"{pct:.2f}%")
        with col3:
            st.metric("📈 القيمة السوقية", f"${info.get('marketCap', 0):,.0f}")
        with col4:
            st.metric("📊 نسبة PE", info.get("trailingPE", "N/A"))

        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="السعر",
            )
        )

        if len(df) > 20:
            ma20 = df["Close"].rolling(20).mean()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=ma20,
                    line=dict(color="#FFD700", width=1.5),
                    name="MA20",
                )
            )

        fig.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=False,
        )
        st.plotly_chart(fig, use_container_width=True)


def render_indices():
    st.markdown("### 📊 المؤشرات الأمريكية")
    if st.button("🔄 تحديث المؤشرات", key="refresh_indices"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("جاري جلب بيانات المؤشرات..."):
        indices_data = {}
        for symbol, name in US_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="1d")
                info = ticker.info
                if not history.empty:
                    current = history["Close"].iloc[-1]
                    prev = info.get("previousClose", current)
                    change = current - prev
                    pct = (change / prev) * 100 if prev > 0 else 0
                else:
                    current, change, pct = 0, 0, 0

                indices_data[symbol] = {
                    "symbol": symbol,
                    "name": name,
                    "price": current,
                    "change": change,
                    "change_percent": pct,
                }
            except:
                continue

        cols = st.columns(4)
        for idx, (symbol, data) in enumerate(indices_data.items()):
            with cols[idx % 4]:
                color = (
                    "#00E676" if data["change_percent"] > 0 else "#FF5252"
                )
                st.markdown(
                    f"""
                <div class="gradient-card">
                    <div class="card-title">{symbol} - {data['name']}</div>
                    <div class="card-value">${data['price']:,.2f}</div>
                    <div class="card-sub" style="color:{color} !important;">{data['change']:+.2f} ({data['change_percent']:+.2f}%)</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def render_etfs():
    st.markdown("### 🏦 الصناديق المتداولة (ETFs)")
    etf_groups = {
        "الكل": list(POPULAR_ETFS.keys()),
        "أسهم": ["SPY", "QQQ", "DIA", "IWM", "VTI", "VOO"],
        "سندات": ["BND", "AGG", "TLT"],
        "سلع": ["GLD", "SLV", "USO"],
        "مضاعف": ["TQQQ", "SQQQ", "UPRO"],
    }

    selected_group = st.selectbox(
        "تصفية حسب النوع:", list(etf_groups.keys()), key="etf_group"
    )

    with st.spinner("جاري جلب بيانات الصناديق..."):
        df = fetch_multiple_stocks(etf_groups[selected_group])
        if df.empty:
            st.warning("⚠️ لا توجد بيانات متاحة")
            return

        display_df = df.copy()
        display_df["price"] = display_df["price"].apply(
            lambda x: f"${x:.2f}" if isinstance(x, (int, float)) and x > 0 else "N/A"
        )
        display_df["change_percent"] = display_df["change_percent"].apply(
            lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else "0.00%"
        )

        st.dataframe(
            display_df[
                ["symbol", "name", "price", "change_percent", "volume"]
            ],
            column_config={
                "symbol": "الرمز",
                "name": "الاسم",
                "price": "السعر",
                "change_percent": "التغير %",
                "volume": "حجم التداول",
            },
            use_container_width=True,
            hide_index=True,
        )


def render_search():
    st.markdown("### 🔍 بحث شامل")
    search_term = st.text_input(
        "ابحث عن رمز أو اسم شركة:",
        placeholder="مثال: AAPL, Microsoft...",
        key="search_input",
    )

    if search_term:
        search_term = search_term.upper().strip()
        results = []

        for symbol, name in POPULAR_STOCKS.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append({"type": "📈 سهم", "symbol": symbol, "name": name})

        for symbol, name in US_INDICES.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append(
                    {"type": "📊 مؤشر", "symbol": symbol, "name": name}
                )

        for symbol, name in POPULAR_ETFS.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append(
                    {"type": "🏦 صندوق", "symbol": symbol, "name": name}
                )

        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            st.dataframe(
                pd.DataFrame(results), use_container_width=True, hide_index=True
            )
            selected = st.selectbox(
                "اختر رمزاً للتحليل:",
                [r["symbol"] for r in results],
                key="search_result_select",
            )
            if selected:
                display_stock_analysis(selected)
        else:
            st.warning(f"⚠️ لا توجد نتائج لـ '{search_term}'")


if __name__ == "__main__":
    render()
