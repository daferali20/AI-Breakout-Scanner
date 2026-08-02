# backend/analysis/indicators.py
"""
حساب المؤشرات الفنية المتقدمة
"""

import pandas as pd
import numpy as np
from typing import Dict

class TechnicalIndicators:
    """حساب المؤشرات الفنية"""
    
    def calculate_all(self, df: pd.DataFrame) -> Dict:
        """حساب جميع المؤشرات"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        return {
            'rsi': self._calculate_rsi(close),
            'rsi_score': self._rsi_score(close),
            'volume_ratio': self._volume_ratio(volume),
            'volume_score': self._volume_score(volume),
            'volatility_score': self._volatility_score(df),
            'price_position': self._price_position(close, high)
        }
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
        loss = loss.replace(0, np.nan)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50
    
    def _rsi_score(self, close: pd.Series) -> float:
        rsi = self._calculate_rsi(close)
        if 40 <= rsi <= 60:
            return 70
        elif 30 <= rsi <= 70:
            return 50
        else:
            return max(0, 100 - abs(rsi - 50) * 2)
    
    def _volume_ratio(self, volume: pd.Series) -> float:
        avg = volume.iloc[-21:-1].mean()
        return volume.iloc[-1] / avg if avg > 0 else 1
    
    def _volume_score(self, volume: pd.Series) -> float:
        ratio = self._volume_ratio(volume)
        return min(100, ratio * 40)
    
    def _volatility_score(self, df: pd.DataFrame) -> float:
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean().iloc[-1] or 0
        
        current_price = close.iloc[-1]
        atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
        return min(100, atr_percent * 10)
    
    def _price_position(self, close: pd.Series, high: pd.Series) -> float:
        high_52 = high.iloc[-252:].max()
        return (close.iloc[-1] / high_52 * 100) if high_52 > 0 else 50
