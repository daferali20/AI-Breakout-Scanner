# frontend/pages/analyze.py
"""
صفحة تحليل سهم محدد - مع رموز رئيسية وإضافة مخصصة
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================================================================
# قائمة الرموز الرئيسية
# ============================================================================

MAIN_SYMBOLS = {
    # التكنولوجيا
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
    
    # المالية
    'JPM': 'JPMorgan Chase',
    'BAC': 'Bank of America',
    'WFC': 'Wells Fargo',
    'C': 'Citigroup Inc.',
    'GS': 'Goldman Sachs',
    'MS': 'Morgan Stanley',
    'V': 'Visa Inc.',
    'MA': 'Mastercard Inc.',
    
    # الرعاية الصحية
    'JNJ': 'Johnson & Johnson',
    'UNH': 'UnitedHealth',
    'PFE': 'Pfizer Inc.',
    'ABBV': 'AbbVie Inc.',
    'MRK': 'Merck & Co.',
    'TMO': 'Thermo Fisher',
    'ABT': 'Abbott Laboratories',
    'DHR': 'Danaher Corp.',
    
    # الاستهلاك
    'WMT': 'Walmart Inc.',
    'PG': 'Procter & Gamble',
    'KO': 'Coca-Cola Co.',
    'PEP': 'PepsiCo Inc.',
    'COST': 'Costco Wholesale',
    'MCD': "McDonald's Corp.",
    'NKE': 'Nike Inc.',
    'SBUX': 'Starbucks Corp.',
    'HD': 'Home Depot',
    
    # الطاقة والصناعة
    'XOM': 'Exxon Mobil',
    'CVX': 'Chevron Corp.',
    'COP': 'ConocoPhillips',
    'BA': 'Boeing Co.',
    'CAT': 'Caterpillar Inc.',
    'GE': 'General Electric',
    'HON': 'Honeywell International',
    
    # الاتصالات
    'T': 'AT&T Inc.',
    'VZ': 'Verizon Communications',
    'TMUS': 'T-Mobile US',
    
    # العقارات
    'AMT': 'American Tower',
    'PLD': 'Prologis Inc.',
    'CCI': 'Crown Castle',
    'EQIX': 'Equinix Inc.'
}

# ============================================================================
# دوال جلب البيانات
# ============================================================================

@st.cache_data(ttl=60)
def fetch_stock_data(symbol, period="3mo", interval="1d"):
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
def fetch_company_news(symbol, limit=5):
    """جلب أخبار الشركة"""
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if news:
            return news[:limit]
        return []
    except:
        return []

# ============================================================================
# دوال عرض البيانات
# ============================================================================

def create_candlestick_chart(df, symbol, title=""):
    """إنشاء رسم بياني للشموع"""
    fig = go.Figure()
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر",
        increasing=dict(line=dict(color='#00E676')),
        decreasing=dict(line=dict(color='#FF5252'))
    ))
    
    # المتوسطات المتحركة
    if len(df) > 20:
        ma20 = df['Close'].rolling(20).mean()
        ma50 = df['Close'].rolling(50).mean() if len(df) > 50 else None
        ma200 = df['Close'].rolling(200).mean() if len(df) > 200 else None
        
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
        
        if ma200 is not None:
            fig.add_trace(go.Scatter(
                x=df.index, y=ma200,
                line=dict(color='#AB47BC', width=1.5),
                name="MA200"
            ))
    
    # حجم التداول
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name="حجم التداول",
        marker=dict(color='rgba(102, 126, 234, 0.3)'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=title or f"📈 {symbol} - رسم بياني فني",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(title="السعر"),
        yaxis2=dict(
            title="الحجم",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified'
    )
    
    return fig

def display_stock_info(info):
    """عرض معلومات الشركة"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">🏢 القطاع</div>
            <div style="font-weight: 600; font-size: 1.1rem;">{info.get('sector', 'غير معروف')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">📊 الصناعة</div>
            <div style="font-weight: 600; font-size: 1.1rem;">{info.get('industry', 'غير معروف')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">📍 البلد</div>
            <div style="font-weight: 600; font-size: 1.1rem;">{info.get('country', 'غير معروف')}</div>
        </div>
        """, unsafe_allow_html=True)

def display_news(news_items):
    """عرض أخبار الشركة"""
    if not news_items:
        st.info("📰 لا توجد أخبار حديثة")
        return
    
    for item in news_items[:3]:
        title = item.get('title', 'عنوان غير معروف')
        link = item.get('link', '#')
        publisher = item.get('publisher', 'مصدر غير معروف')
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; border-right: 3px solid #667eea;">
            <div style="font-weight: 600;">📰 {title}</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">{publisher}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# الصفحة الرئيسية
# ============================================================================

def render():
    """عرض صفحة تحليل السهم"""
    st.subheader("📈 تحليل سهم محدد")
    
    # ====================================================================
    # اختيار الرمز - مع رموز رئيسية وإضافة مخصصة
    # ====================================================================
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <p style="margin:0; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
            💡 اختر من الرموز الرئيسية أو اكتب رمزاً مخصصاً
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # صف الإدخال
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # قائمة الرموز الرئيسية مع خيار إدخال مخصص
        symbol_options = ["-- اختر رمزاً --"] + list(MAIN_SYMBOLS.keys()) + ["✏️ إدخال مخصص"]
        
        selected_option = st.selectbox(
            "اختر رمز السهم:",
            options=symbol_options,
            index=0,
            key="symbol_select"
        )
        
        # إذا اختار المستخدم "إدخال مخصص" أو ليس رمزاً رئيسياً
        if selected_option == "✏️ إدخال مخصص":
            symbol = st.text_input(
                "أدخل رمز السهم:",
                value="",
                placeholder="مثال: AAPL, MSFT, TSLA...",
                key="custom_symbol"
            ).upper().strip()
        elif selected_option != "-- اختر رمزاً --":
            symbol = selected_option
        else:
            symbol = ""
    
    with col2:
        # زر التحديث بجانب الإدخال
        st.markdown("<br>", unsafe_allow_html=True)  # مسافة
        refresh_clicked = st.button(
            "🔄 تحديث",
            type="primary",
            width="stretch",
            key="refresh_analysis"
        )
    
    # إذا كان هناك رمز محدد
    if symbol:
        display_analysis(symbol, refresh_clicked)
    else:
        st.info("🔍 اختر أو اكتب رمز سهم للبدء")

# ============================================================================
# عرض التحليل
# ============================================================================

def display_analysis(symbol, refresh=False):
    """عرض تحليل السهم"""
    
    # إذا تم الضغط على تحديث، نمسح الكاش
    if refresh:
        st.cache_data.clear()
    
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        # جلب البيانات
        df = fetch_stock_data(symbol, period="6mo")
        
        if df.empty:
            st.error(f"❌ لا توجد بيانات للسهم {symbol}")
            st.info("💡 تأكد من صحة الرمز (مثال: AAPL, MSFT, TSLA)")
            return
        
        info = fetch_stock_info(symbol)
        news = fetch_company_news(symbol)
        
        # ============================================================
        # معلومات أساسية
        # ============================================================
        
        company_name = info.get('longName', symbol)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                    padding: 15px 20px; border-radius: 12px; border: 1px solid rgba(102,126,234,0.2); margin-bottom: 20px;">
            <h3 style="margin:0; color: #ffffff;">{symbol} - {company_name}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # معلومات الشركة
        display_stock_info(info)
        
        st.markdown("---")
        
        # ============================================================
        # بطاقات المؤشرات
        # ============================================================
        
        current_price = df['Close'].iloc[-1]
        previous_close = info.get('previousClose', current_price)
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 السعر الحالي",
                f"${current_price:.2f}",
                delta=f"{change:+.2f} ({change_percent:+.2f}%)"
            )
        
        with col2:
            high_52 = info.get('fiftyTwoWeekHigh', 0)
            low_52 = info.get('fiftyTwoWeekLow', 0)
            st.metric(
                "📈 أعلى 52 أسبوع",
                f"${high_52:.2f}" if high_52 else "N/A",
                delta=f"{(current_price/high_52*100 - 100):+.1f}%" if high_52 else None
            )
        
        with col3:
            st.metric(
                "📉 أدنى 52 أسبوع",
                f"${low_52:.2f}" if low_52 else "N/A",
                delta=f"{(current_price/low_52*100 - 100):+.1f}%" if low_52 else None
            )
        
        with col4:
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 0)
            vol_ratio = volume / avg_volume if avg_volume > 0 else 0
            st.metric(
                "📊 حجم التداول",
                f"{volume:,}",
                delta=f"{vol_ratio:.1f}x المتوسط"
            )
        
        st.markdown("---")
        
        # ============================================================
        # رسم بياني
        # ============================================================
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # الرسم البياني
            fig = create_candlestick_chart(df, symbol)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # مؤشرات سريعة
            st.markdown("#### 📊 مؤشرات سريعة")
            
            # حساب RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0.0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
            loss = loss.replace(0, float('nan'))
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50
            
            st.metric("RSI (14)", f"{current_rsi:.1f}")
            
            # حجم التداول
            avg_volume = df['Volume'].iloc[-21:-1].mean() if len(df) > 21 else df['Volume'].mean()
            vol_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
            st.metric("نسبة الحجم", f"{vol_ratio:.2f}x")
            
            # التقلبات
            atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or 0
            atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
            st.metric("ATR", f"${atr:.2f} ({atr_percent:.1f}%)")
            
            # نسبة PE
            pe = info.get('trailingPE', 'N/A')
            st.metric("نسبة PE", pe if pe == 'N/A' else f"{pe:.2f}")
            
            # توزيعات الأرباح
            dividend = info.get('dividendRate', 0)
            if dividend > 0:
                dividend_yield = info.get('dividendYield', 0) * 100
                st.metric("توزيعات الأرباح", f"${dividend:.2f}", delta=f"{dividend_yield:.2f}%")
            else:
                st.metric("توزيعات الأرباح", "لا توجد")
        
        st.markdown("---")
        
        # ============================================================
        # أخبار الشركة
        # ============================================================
        
        with st.expander("📰 آخر الأخبار", expanded=False):
            display_news(news)
        
        st.markdown("---")
        
        # ============================================================
        # رموز مشابهة
        # ============================================================
        
        with st.expander("🔗 رموز مشابهة", expanded=False):
            sector = info.get('sector', '')
            similar_symbols = []
            
            for sym, name in MAIN_SYMBOLS.items():
                if sym != symbol:
                    similar_symbols.append(sym)
            
            if similar_symbols:
                cols = st.columns(8)
                for i, sym in enumerate(similar_symbols[:16]):
                    with cols[i % 8]:
                        if st.button(sym, key=f"similar_{sym}"):
                            st.session_state.custom_symbol = sym
                            st.rerun()
            else:
                st.info("لا توجد رموز مشابهة")

# ============================================================================
# دالة لإضافة رمز جديد
# ============================================================================

def add_custom_symbol(symbol, name=""):
    """إضافة رمز مخصص إلى القائمة"""
    if symbol and symbol not in MAIN_SYMBOLS:
        MAIN_SYMBOLS[symbol] = name or symbol
        return True
    return False
