"""
حساب المؤشرات الفنية المتقدمة - AI Breakout Scanner
"""

import pandas as pd
import numpy as np
from typing import Dict


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """حساب مؤشرات Bollinger Bands و Keltner Channels واكتشاف الضغط (Squeeze)"""
    df = df.copy()
    
    # تأكد من وجود الحد الأدنى من الصفوف
    if len(df) < 20:
        df['SMA20'] = np.nan
        df['STD20'] = np.nan
        df['BB_Upper'] = np.nan
        df['BB_Lower'] = np.nan
        df['ATR20'] = np.nan
        df['KC_Upper'] = np.nan
        df['KC_Lower'] = np.nan
        df['Squeeze_On'] = False
        return df

    # حساب المتوسط المتحرك البسيط (SMA 20) والانحراف المعياري
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    
    # Bollinger Bands
    df['BB_Upper'] = df['SMA20'] + (df['STD20'] * 2)
    df['BB_Lower'] = df['SMA20'] - (df['STD20'] * 2)
    
    # Average True Range (ATR 20)
    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['ATR20'] = df['TR'].rolling(window=20).mean()
    
    # Keltner Channels
    df['KC_Upper'] = df['SMA20'] + (df['ATR20'] * 1.5)
    df['KC_Lower'] = df['SMA20'] - (df['ATR20'] * 1.5)
    
    # Squeeze Condition (Bollinger Bands داخل Keltner Channels)
    df['Squeeze_On'] = (df['BB_Upper'] < df['KC_Upper']) & (df['BB_Lower'] > df['KC_Lower'])
    
    return df


class TechnicalIndicators:
    """كلاس حساب ودرجات المؤشرات الفنية لكشف الاختراقات"""
    
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, float]:
        """حساب جميع المؤشرات وإعادة النواتج على شكل قاموس"""
        if df.empty or len(df) < 14:
            return {
                'rsi': 50.0,
                'rsi_score': 50.0,
                'volume_ratio': 1.0,
                'volume_score': 50.0,
                'volatility_score': 50.0,
                'price_position': 50.0,
                'squeeze_on': False
            }

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # حساب السكويز بالاستفادة من الدالة
        df_ind = calculate_indicators(df)
        squeeze_on = bool(df_ind['Squeeze_On'].iloc[-1]) if 'Squeeze_On' in df_ind.columns else False
        
        return {
            'rsi': round(self._calculate_rsi(close), 2),
            'rsi_score': round(self._rsi_score(close), 2),
            'volume_ratio': round(self._volume_ratio(volume), 2),
            'volume_score': round(self._volume_score(volume), 2),
            'volatility_score': round(self._volatility_score(df), 2),
            'price_position': round(self._price_position(close, high), 2),
            'squeeze_on': squeeze_on
        }
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """حساب مؤشر القوة النسبية RSI"""
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
        loss = loss.replace(0, np.nan)
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        val = rsi.iloc[-1]
        return float(val) if not np.isnan(val) else 50.0
    
    def _rsi_score(self, close: pd.Series) -> float:
        """تقييم درجة الـ RSI للاختراق السعري"""
        rsi = self._calculate_rsi(close)
        if 45 <= rsi <= 65:
            return 85.0  # نطاق مثالي للاختراق
        elif 35 <= rsi <= 70:
            return 60.0
        else:
            return max(0.0, float(100 - abs(rsi - 50) * 2))
    
    def _volume_ratio(self, volume: pd.Series) -> float:
        """مقارنة حجم التداول الحالي بمتوسط 20 يوماً سابقاً"""
        if len(volume) < 21:
            avg = volume.mean()
        else:
            avg = volume.iloc[-21:-1].mean()
            
        current_vol = volume.iloc[-1]
        return float(current_vol / avg) if avg > 0 else 1.0
    
    def _volume_score(self, volume: pd.Series) -> float:
        """تقييم حجم التداول"""
        ratio = self._volume_ratio(volume)
        return min(100.0, ratio * 40)
    
    def _volatility_score(self, df: pd.DataFrame) -> float:
        """حساب درجة التقلب بناءً على ATR"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)  # إصلاح تحذير numpy
        
        atr_series = true_range.rolling(14).mean()
        atr = atr_series.iloc[-1] if not atr_series.empty and not np.isnan(atr_series.iloc[-1]) else 0.0
        
        current_price = close.iloc[-1]
        atr_percent = (atr / current_price) * 100 if current_price > 0 else 0.0
        return min(100.0, atr_percent * 10)
    
    def _price_position(self, close: pd.Series, high: pd.Series) -> float:
        """حساب موقع السعر الحالي بالنسبة لأعلى سعر (52 أسبوع)"""
        window = min(len(high), 252)
        high_52 = high.iloc[-window:].max()
        current_close = close.iloc[-1]
        
        return float((current_close / high_52) * 100) if high_52 > 0 else 50.0
