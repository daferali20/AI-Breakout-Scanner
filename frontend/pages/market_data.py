# frontend/pages/market_data.py
"""
صفحة بيانات السوق الأمريكية - جلب وعرض الأسهم والمؤشرات والصناديق
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

def render():
    """عرض صفحة بيانات السوق"""
    st.subheader("📊 بيانات السوق الأمريكية")
    
    # تبويبات للتصنيفات المختلفة
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 الأسهم", 
        "📊 المؤشرات", 
        "🏦 الصناديق", 
        "🔍 بحث شامل"
    ])
    
    with tab1:
        render_stocks()
    
    with tab2:
        render_indices()
    
    with tab3:
        render_etfs()
    
    with tab4:
        render_search()

# ============================================================================
# البيانات الأساسية
# ============================================================================

# قائمة المؤشرات الأمريكية
US_INDICES = {
    '^GSPC': 'S&P 500',
    '^DJI': 'Dow Jones',
    '^IXIC': 'NASDAQ',
    '^RUT': 'Russell 2000',
    '^VIX': 'VIX - التقلبات',
    '^FTSE': 'FTSE 100',
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng'
}

# قائمة الصناديق المتداولة (ETFs) الشهيرة
POPULAR_ETFS = {
    'SPY': 'S&P 500 ETF',
    'QQQ': 'NASDAQ 100 ETF',
    'DIA': 'Dow Jones ETF',
    'IWM': 'Russell 2000 ETF',
    'VTI': 'Total Stock Market',
    'VOO': 'S&P 500 Vanguard',
    'BND': 'Total Bond Market',
    'GLD': 'Gold ETF',
    'SLV': 'Silver ETF',
    'USO': 'Oil ETF',
    'TQQQ': 'NASDAQ 3x Bull',
    'SQQQ': 'NASDAQ 3x Bear'
}

# قائمة الأسهم الأمريكية الشهيرة
POPULAR_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corp.',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corp.',
    'META': 'Meta Platforms',
    'TSLA': 'Tesla Inc.',
    'AMD': 'Advanced Micro Devices',
    'INTC': 'Intel Corp.',
    'NFLX': 'Netflix Inc.',
    'PYPL': 'PayPal Holdings',
    'ADBE': 'Adobe Inc.',
    'CRM': 'Salesforce Inc.',
    'ORCL': 'Oracle Corp.',
    'IBM': 'IBM Corp.',
    'CSCO': 'Cisco Systems',
    'QCOM': 'Qualcomm Inc.',
    'TXN': 'Texas Instruments',
    'AVGO': 'Broadcom Inc.',
    'JPM': 'JPMorgan Chase',
    'BAC': 'Bank of America',
    'WFC': 'Wells Fargo',
    'JNJ': 'Johnson & Johnson',
    'UNH': 'UnitedHealth',
    'PFE': 'Pfizer Inc.',
    'WMT': 'Walmart Inc.',
    'PG': 'Procter & Gamble',
    'KO': 'Coca-Cola Co.',
    'XOM': 'Exxon Mobil',
    'CVX': 'Chevron Corp.'
}

# ============================================================================
# دوال جلب البيانات
# ============================================================================

@st.cache_data(ttl=60)  # تحديث كل دقيقة
def fetch_stock_data(symbol, period="1d", interval="1m"):
    """جلب بيانات السهم"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_stock_info(symbol):
    """جلب معلومات السهم"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except:
        return {}

@st.cache_data(ttl=60)
def fetch_multiple_stocks(symbols):
    """جلب بيانات عدة أسهم"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")
            
            if not history.empty:
                current_price = history['Close'].iloc[-1]
                previous_close = ticker.info.get('previousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            else:
                current_price = 0
                change = 0
                change_percent = 0
            
            data[symbol] = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'غير معروف'),
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend': info.get('dividendRate', 0),
                'high_52': info.get('fiftyTwoWeekHigh', 0),
                'low_52': info.get('fiftyTwoWeekLow', 0)
            }
        except:
            continue
    
    return pd.DataFrame(data).T

# ============================================================================
# عرض الأسهم
# ============================================================================

def render_stocks():
    """عرض الأسهم الأمريكية"""
    st.markdown("### 📈 الأسهم الأمريكية")
    
    # اختيار القطاع
    sectors = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة", "الصناعة"]
    selected_sector = st.selectbox("تصفية حسب القطاع:", sectors, key="stock_sector")
    
    # عدد الأسهم
    col1, col2 = st.columns([3, 1])
    with col2:
        max_stocks = st.number_input("عدد الأسهم:", min_value=5, max_value=50, value=20, step=5, key="stock_count")
    
    # جلب البيانات
    with st.spinner("جاري جلب بيانات الأسهم..."):
        # اختيار الأسهم
        stocks_to_fetch = list(POPULAR_STOCKS.keys())[:max_stocks]
        df = fetch_multiple_stocks(stocks_to_fetch)
        
        if df.empty:
            st.warning("⚠️ لا توجد بيانات متاحة حالياً")
            return
        
        # تصفية حسب القطاع
        if selected_sector != "الكل":
            df = df[df['sector'] == selected_sector]
        
        # عرض الجدول
        display_stock_table(df)
    
    # تحليل سهم محدد
    st.markdown("---")
    st.markdown("### 🔍 تحليل سهم محدد")
    
    selected_symbol = st.selectbox(
        "اختر سهماً للتحليل:",
        list(POPULAR_STOCKS.keys()),
        key="stock_select_analysis"
    )
    
    if selected_symbol:
        display_stock_analysis(selected_symbol)

def display_stock_table(df):
    """عرض جدول الأسهم"""
    if df.empty:
        st.info("لا توجد أسهم في هذا القطاع")
        return
    
    # تنسيق الأعمدة
    display_df = df.copy()
    
    # تنسيق الأرقام
    display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
    display_df['change'] = display_df['change'].apply(lambda x: f"${x:.2f}" if x != 0 else "$0.00")
    display_df['change_percent'] = display_df['change_percent'].apply(lambda x: f"{x:.2f}%")
    
    # تلوين التغيرات
    def color_change(val):
        if isinstance(val, str) and '%' in val:
            try:
                num = float(val.replace('%', ''))
                if num > 0:
                    return 'color: #00E676'
                elif num < 0:
                    return 'color: #FF5252'
            except:
                pass
        return ''
    
    # عرض الجدول
    st.dataframe(
        display_df[['symbol', 'name', 'sector', 'price', 'change', 'change_percent', 'volume']],
        column_config={
            "symbol": "الرمز",
            "name": "الشركة",
            "sector": "القطاع",
            "price": "السعر",
            "change": "التغير",
            "change_percent": "التغير %",
            "volume": "حجم التداول"
        },
        width='stretch',
        hide_index=True
    )

def display_stock_analysis(symbol):
    """عرض تحليل سهم محدد"""
    with st.spinner(f"جاري تحليل {symbol}..."):
        info = fetch_stock_info(symbol)
        df = fetch_stock_data(symbol, period="3mo")
        
        if df.empty:
            st.error(f"❌ لا توجد بيانات للسهم {symbol}")
            return
        
        # معلومات أساسية
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = df['Close'].iloc[-1]
            st.metric("💰 السعر", f"${current_price:.2f}")
        
        with col2:
            change = info.get('previousClose', current_price)
            st.metric("📊 التغير", f"${current_price - change:.2f}", 
                     delta=f"{(current_price - change) / change * 100:.2f}%")
        
        with col3:
            st.metric("📈 القيمة السوقية", f"${info.get('marketCap', 0):,.0f}")
        
        with col4:
            st.metric("📊 نسبة PE", info.get('trailingPE', 'N/A'))
        
        st.markdown("---")
        
        # رسم بياني
        st.markdown("#### 📈 الرسم البياني")
        
        fig = go.Figure()
        
        # شموع
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="السعر"
        ))
        
        # متوسطات
        if len(df) > 20:
            ma20 = df['Close'].rolling(20).mean()
            ma50 = df['Close'].rolling(50).mean() if len(df) > 50 else None
            
            fig.add_trace(go.Scatter(
                x=df.index, y=ma20,
                line=dict(color='#FFD700', width=1.5),
                name="MA20"
            ))
            
            if ma50 is not None:
                fig.add_trace(go.Scatter(
                    x=df.index, y=ma50,
                    line=dict(color='#29B6F6', width=1.5),
                    name="MA50"
                ))
        
        fig.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# عرض المؤشرات
# ============================================================================

def render_indices():
    """عرض المؤشرات الأمريكية"""
    st.markdown("### 📊 المؤشرات الأمريكية")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        if st.button("🔄 تحديث المؤشرات", key="refresh_indices"):
            st.cache_data.clear()
            st.rerun()
    
    # جلب بيانات المؤشرات
    with st.spinner("جاري جلب بيانات المؤشرات..."):
        indices_data = {}
        
        for symbol, name in US_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="1d")
                info = ticker.info
                
                if not history.empty:
                    current = history['Close'].iloc[-1]
                    previous_close = info.get('previousClose', current)
                    change = current - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
                else:
                    current = 0
                    change = 0
                    change_percent = 0
                
                indices_data[symbol] = {
                    'symbol': symbol,
                    'name': name,
                    'price': current,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': info.get('volume', 0)
                }
            except:
                continue
        
        # عرض المؤشرات في بطاقات
        cols = st.columns(4)
        
        for idx, (symbol, data) in enumerate(indices_data.items()):
            with cols[idx % 4]:
                color = "#00E676" if data['change_percent'] > 0 else "#FF5252"
                st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 15px;
                    margin: 5px 0;
                    text-align: center;
                    transition: transform 0.3s ease;
                ">
                    <div style="font-weight:700; font-size:1.1rem;">{symbol}</div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.6);">{data['name']}</div>
                    <div style="font-size:1.5rem; font-weight:800; margin:8px 0;">${data['price']:,.2f}</div>
                    <div style="color:{color}; font-weight:700;">
                        {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# عرض الصناديق (ETFs)
# ============================================================================

def render_etfs():
    """عرض الصناديق المتداولة"""
    st.markdown("### 🏦 الصناديق المتداولة (ETFs)")
    
    # اختيار المجموعة
    etf_groups = {
        "الكل": list(POPULAR_ETFS.keys()),
        "أسهم": ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO'],
        "سندات": ['BND', 'AGG', 'TLT'],
        "سلع": ['GLD', 'SLV', 'USO'],
        "مضاعف": ['TQQQ', 'SQQQ', 'UPRO']
    }
    
    selected_group = st.selectbox(
        "تصفية حسب النوع:",
        list(etf_groups.keys()),
        key="etf_group"
    )
    
    # جلب البيانات
    with st.spinner("جاري جلب بيانات الصناديق..."):
        symbols = etf_groups[selected_group]
        df = fetch_multiple_stocks(symbols)
        
        if df.empty:
            st.warning("⚠️ لا توجد بيانات متاحة")
            return
        
        # عرض الجدول
        display_df = df.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
        display_df['change_percent'] = display_df['change_percent'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(
            display_df[['symbol', 'name', 'price', 'change_percent', 'volume']],
            column_config={
                "symbol": "الرمز",
                "name": "الاسم",
                "price": "السعر",
                "change_percent": "التغير %",
                "volume": "حجم التداول"
            },
            width='stretch',
            hide_index=True
        )

# ============================================================================
# البحث الشامل
# ============================================================================

def render_search():
    """البحث الشامل في جميع الرموز"""
    st.markdown("### 🔍 بحث شامل")
    
    # مربع البحث
    search_term = st.text_input(
        "ابحث عن رمز أو اسم شركة:",
        placeholder="مثال: AAPL, Microsoft, ETF...",
        key="search_input"
    )
    
    if search_term:
        search_term = search_term.upper().strip()
        
        # البحث في جميع القوائم
        results = []
        
        # 1. البحث في الأسهم
        for symbol, name in POPULAR_STOCKS.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append({'type': '📈 سهم', 'symbol': symbol, 'name': name})
        
        # 2. البحث في المؤشرات
        for symbol, name in US_INDICES.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append({'type': '📊 مؤشر', 'symbol': symbol, 'name': name})
        
        # 3. البحث في الصناديق
        for symbol, name in POPULAR_ETFS.items():
            if search_term in symbol or search_term.lower() in name.lower():
                results.append({'type': '🏦 صندوق', 'symbol': symbol, 'name': name})
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            # عرض النتائج
            df = pd.DataFrame(results)
            st.dataframe(df, width='stretch', hide_index=True)
            
            # تحليل الرمز المختار
            selected = st.selectbox(
                "اختر رمزاً للتحليل:",
                [r['symbol'] for r in results],
                key="search_result_select"
            )
            
            if selected:
                display_stock_analysis(selected)
        else:
            st.warning(f"⚠️ لا توجد نتائج لـ '{search_term}'")

# ============================================================================
# دالة للحصول على جميع الرموز
# ============================================================================

def get_all_symbols():
    """الحصول على جميع الرموز في قائمة واحدة"""
    all_symbols = {}
    
    # إضافة الأسهم
    for symbol, name in POPULAR_STOCKS.items():
        all_symbols[symbol] = {'name': name, 'type': 'سهم'}
    
    # إضافة المؤشرات
    for symbol, name in US_INDICES.items():
        all_symbols[symbol] = {'name': name, 'type': 'مؤشر'}
    
    # إضافة الصناديق
    for symbol, name in POPULAR_ETFS.items():
        all_symbols[symbol] = {'name': name, 'type': 'صندوق'}
    
    return all_symbols

# ============================================================================
# دالة للحصول على بيانات السوق لحظياً
# ============================================================================

@st.cache_data(ttl=30)
def get_market_overview():
    """الحصول على نظرة عامة للسوق"""
    try:
        # مؤشرات رئيسية
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ'
        }
        
        data = {}
        for symbol, name in indices.items():
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1d")
            if not history.empty:
                data[name] = {
                    'price': history['Close'].iloc[-1],
                    'change': history['Close'].iloc[-1] - history['Open'].iloc[0]
                }
        
        return data
    except:
        return {}
