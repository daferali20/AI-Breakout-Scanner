# frontend/pages/analyze.py
"""
صفحة تحليل سهم محدد
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

def run_analysis(ticker):
    # محاكاة لعملية الفحص الحسابية والذكاء الاصطناعي
    st.session_state.selected_ticker = ticker
    st.session_state.analysis_data = {
        "ticker": ticker,
        "breakout_score": np.random.randint(60, 99),
        "squeeze_status": "Squeeze On" if np.random.rand() > 0.5 else "Squeeze Off",
        "signal": "BUY (STRONG)" if np.random.rand() > 0.4 else "NEUTRAL"
    }

def render_page():
    st.header("🔍 فحص وتحليل الاختراقات السعرية")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker_input = st.text_input(
            "أدخل رمز السهم (Ticker):", 
            value=st.session_state.get("selected_ticker", "AAPL")
        ).upper()
    
    with col2:
        st.write(" ") # محاذاة عمودية
        st.write(" ")
        # تشغيل الفحص باستخدام callback لضمان الاستجابة السريعة
        st.button(
            "بدء التحليل 🚀", 
            on_click=run_analysis, 
            args=(ticker_input,),
            use_container_width=True
        )

    # عرض النتائج من الـ Session State إذا كانت متوفرة
    if "analysis_data" in st.session_state and st.session_state.analysis_data:
        data = st.session_state.analysis_data
        st.success(f"تم تحليل السهم: **{data['ticker']}** بنجاح!")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("قوة الاختراق المتوقعة", f"{data['breakout_score']}%")
        m2.metric("حالة ضغط Bollinger/Keltner", data['squeeze_status'])
        m3.metric("توصية النموذج الذكي", data['signal'])
def render():
    """عرض صفحة تحليل السهم"""
    st.subheader("📈 تحليل سهم محدد")
    
    # الرموز الرئيسية
    MAIN_SYMBOLS = {
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
        'CVX': 'Chevron Corp.',
        'V': 'Visa Inc.',
        'MA': 'Mastercard Inc.'
    }
    
    # إضافة الرموز المخصصة
    if 'custom_symbols' in st.session_state:
        MAIN_SYMBOLS.update(st.session_state.custom_symbols)
    
    # معلومات مساعدة
    st.markdown("""
    <div style="background: rgba(255,255,255,0.02); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <p style="margin:0; color: rgba(255,255,255,0.6); font-size: 0.85rem;">
            💡 اختر من الرموز الرئيسية أو اكتب رمزاً مخصصاً (مثل: AAPL, MSFT, TSLA)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # إدخال الرمز
    symbol = get_symbol_input(MAIN_SYMBOLS)
    
    # عرض التحليل
    if symbol:
        display_stock_analysis(symbol)
    else:
        st.info("🔍 اختر أو اكتب رمز سهم للبدء")

def get_symbol_input(MAIN_SYMBOLS):
    """الحصول على رمز السهم من المستخدم"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        symbol_options = ["-- اختر رمزاً --"] + list(MAIN_SYMBOLS.keys()) + ["✏️ إدخال مخصص"]
        
        selected_option = st.selectbox(
            "اختر رمز السهم:",
            options=symbol_options,
            index=0,
            key="symbol_select_main"
        )
        
        if selected_option == "✏️ إدخال مخصص":
            symbol = st.text_input(
                "أدخل رمز السهم:",
                value=st.session_state.get('custom_symbol_input', ''),
                placeholder="مثال: AAPL, MSFT, TSLA...",
                key="custom_symbol_input_main"
            ).upper().strip()
            
            if symbol and symbol not in MAIN_SYMBOLS:
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if st.button("➕ إضافة", key="add_symbol_main"):
                        st.session_state.custom_symbols[symbol] = symbol
                        st.session_state.custom_symbol_input = symbol
                        st.success(f"✅ تم إضافة {symbol}")
                        st.rerun()
        elif selected_option != "-- اختر رمزاً --":
            symbol = selected_option
            st.session_state.custom_symbol_input = symbol
        else:
            symbol = ""
    
    with col2:
        if symbol and symbol in MAIN_SYMBOLS:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; margin-top: 25px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">🏢 الشركة</div>
                <div style="font-weight: 600; font-size: 1rem;">{MAIN_SYMBOLS[symbol]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_clicked = st.button(
            "🔄 تحديث",
            type="primary",
            width="stretch",
            key="refresh_analysis_main"
        )
        
        if refresh_clicked:
            st.cache_data.clear()
    
    return symbol

def display_stock_analysis(symbol):
    """عرض تحليل السهم"""
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            
            if df.empty:
                st.error(f"❌ لا توجد بيانات للسهم {symbol}")
                return
            
            info = ticker.info
            
            # معلومات أساسية
            display_company_info(symbol, info)
            
            # بطاقات المؤشرات
            display_metrics(df, info)
            
            st.markdown("---")
            
            # رسم بياني
            display_chart(df, symbol)
            
            st.markdown("---")
            
            # أخبار الشركة
            display_news(ticker)
            
        except Exception as e:
            st.error(f"❌ خطأ في التحليل: {str(e)}")
            st.info("💡 تأكد من صحة الرمز (مثال: AAPL, MSFT, TSLA)")

def display_company_info(symbol, info):
    """عرض معلومات الشركة"""
    company_name = info.get('longName', symbol)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                padding: 15px 20px; border-radius: 12px; border: 1px solid rgba(102,126,234,0.2); margin-bottom: 20px;">
        <h3 style="margin:0; color: #ffffff;">{symbol} - {company_name}</h3>
        <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 4px;">
            🏢 {info.get('sector', 'غير معروف')} | 📊 {info.get('industry', 'غير معروف')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_metrics(df, info):
    """عرض بطاقات المؤشرات"""
    current_price = df['Close'].iloc[-1]
    previous_close = info.get('previousClose', current_price)
    change = current_price - previous_close
    change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if change >= 0 else "inverse"
        st.metric(
            "💰 السعر الحالي",
            f"${current_price:.2f}",
            delta=f"{change:+.2f} ({change_percent:+.2f}%)",
            delta_color=delta_color
        )
    
    with col2:
        high_52 = info.get('fiftyTwoWeekHigh', 0)
        if high_52:
            st.metric(
                "📈 أعلى 52 أسبوع",
                f"${high_52:.2f}",
                delta=f"{(current_price/high_52*100 - 100):+.1f}%"
            )
        else:
            st.metric("📈 أعلى 52 أسبوع", "N/A")
    
    with col3:
        low_52 = info.get('fiftyTwoWeekLow', 0)
        if low_52:
            st.metric(
                "📉 أدنى 52 أسبوع",
                f"${low_52:.2f}",
                delta=f"{(current_price/low_52*100 - 100):+.1f}%"
            )
        else:
            st.metric("📉 أدنى 52 أسبوع", "N/A")
    
    with col4:
        volume = info.get('volume', 0)
        avg_volume = info.get('averageVolume', 0)
        if avg_volume > 0:
            vol_ratio = volume / avg_volume
            st.metric(
                "📊 حجم التداول",
                f"{volume:,}",
                delta=f"{vol_ratio:.1f}x المتوسط"
            )
        else:
            st.metric("📊 حجم التداول", f"{volume:,}")

def display_chart(df, symbol):
    """عرض الرسم البياني"""
    fig = go.Figure()
    
    # شموع
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
    
    # متوسطات متحركة
    if len(df) > 20:
        ma20 = df['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20,
            line=dict(color='#FFD700', width=1.5),
            name="MA20"
        ))
    
    if len(df) > 50:
        ma50 = df['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50,
            line=dict(color='#29B6F6', width=1.5),
            name="MA50"
        ))
    
    fig.update_layout(
        title=f"📈 {symbol} - رسم بياني فني",
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
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # مؤشرات سريعة
    display_quick_indicators(df)

def display_quick_indicators(df):
    """عرض مؤشرات سريعة"""
    st.markdown("#### 📊 مؤشرات سريعة")
    
    current_price = df['Close'].iloc[-1]
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    loss = loss.replace(0, float('nan'))
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rsi_color = "#00E676" if 40 <= current_rsi <= 70 else "#FF5252" if current_rsi > 70 else "#FFC107"
        st.metric("RSI (14)", f"{current_rsi:.1f}", delta_color="off")
    
    with col2:
        avg_volume = df['Volume'].iloc[-21:-1].mean() if len(df) > 21 else df['Volume'].mean()
        vol_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
        vol_color = "#00E676" if vol_ratio > 1.5 else "#FFC107" if vol_ratio > 1 else "#FF5252"
        st.metric("نسبة الحجم", f"{vol_ratio:.2f}x")
    
    with col3:
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or 0
        atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
        st.metric("ATR", f"${atr:.2f} ({atr_percent:.1f}%)")
    
    with col4:
        pe = info.get('trailingPE', 'N/A')
        st.metric("نسبة PE", f"{pe:.2f}" if pe != 'N/A' else 'N/A')

def display_news(ticker):
    """عرض أخبار الشركة"""
    with st.expander("📰 آخر الأخبار", expanded=False):
        try:
            news = ticker.news
            if news:
                for item in news[:3]:
                    title = item.get('title', 'عنوان غير معروف')
                    publisher = item.get('publisher', 'مصدر غير معروف')
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; border-right: 3px solid #667eea;">
                        <div style="font-weight: 600;">📰 {title}</div>
                        <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">{publisher}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📰 لا توجد أخبار حديثة")
        except:
            st.info("📰 لا توجد أخبار متاحة")
