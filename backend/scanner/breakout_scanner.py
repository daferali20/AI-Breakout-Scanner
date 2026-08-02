# backend/scanner/breakout_scanner.py
"""
الماسح الرئيسي للانفجارات السعرية
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import yfinance as yf
from backend.analysis.squeeze_detector import SqueezeDetector
from backend.analysis.indicators import TechnicalIndicators

class BreakoutScanner:
    """الماسح الرئيسي لاكتشاف فرص الانفجار السعري"""
    
    def __init__(self):
        self.squeeze = SqueezeDetector()
        self.indicators = TechnicalIndicators()
    
    def scan_stock(self, symbol: str, df: pd.DataFrame = None) -> Dict:
        """مسح سهم واحد"""
        if df is None:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="6mo")
            except:
                return {'error': f'لا يمكن جلب بيانات السهم {symbol}'}
        
        if df.empty or len(df) < 50:
            return {'error': f'بيانات غير كافية للسهم {symbol}'}
        
        try:
            # 1. تحليل الانضغاط
            squeeze_result = self.squeeze.detect(df)
            if 'error' in squeeze_result:
                return squeeze_result
            
            # 2. المؤشرات الفنية
            indicators = self.indicators.calculate_all(df)
            
            # 3. جمع المؤشرات
            all_indicators = {
                **squeeze_result,
                **indicators,
                'current_price': df['Close'].iloc[-1]
            }
            
            # 4. حساب الدرجة النهائية
            total_score = self._calculate_score(all_indicators)
            
            # 5. مستويات التداول
            levels = self._calculate_levels(df)
            
            return {
                'symbol': symbol,
                'score': total_score,
                'squeeze': squeeze_result,
                'indicators': indicators,
                'levels': levels,
                'recommendation': self._get_recommendation(total_score)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_score(self, indicators: Dict) -> float:
        """حساب الدرجة النهائية"""
        weights = {
            'squeeze': 0.40,
            'volatility': 0.15,
            'volume': 0.20,
            'rsi': 0.15,
            'price': 0.10
        }
        
        score = (
            indicators.get('squeeze_score', 0) * weights['squeeze'] +
            indicators.get('volatility_score', 0) * weights['volatility'] +
            indicators.get('volume_score', 0) * weights['volume'] +
            indicators.get('rsi_score', 0) * weights['rsi'] +
            indicators.get('price_position', 50) * weights['price']
        )
        
        return round(min(100, max(0, score)), 2)
    
    def _calculate_levels(self, df: pd.DataFrame) -> Dict:
        """حساب مستويات التداول"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        current = close.iloc[-1]
        atr = (high - low).rolling(14).mean().iloc[-1] or current * 0.02
        resistance = high.iloc[-20:].max()
        support = low.iloc[-20:].min()
        
        return {
            'current': round(current, 2),
            'entry': round(resistance + (atr * 0.5), 2),
            'stop_loss': round(current - (atr * 1.5), 2),
            'target_1': round(current + (atr * 2), 2),
            'target_2': round(current + (atr * 3.5), 2)
        }
    
    def _get_recommendation(self, score: float) -> Dict:
        """توليد التوصية"""
        if score >= 75:
            return {'action': '🟢 شراء قوي', 'risk': 'منخفض'}
        elif score >= 60:
            return {'action': '🟡 شراء', 'risk': 'متوسط'}
        elif score >= 45:
            return {'action': '🔍 مراقبة', 'risk': 'متوسط'}
        else:
            return {'action': '🔴 تجنب', 'risk': 'مرتفع'}
    
    def scan_market(self, symbols: List[str], min_score: float = 60) -> pd.DataFrame:
        """مسح السوق بالكامل"""
        results = []
        
        for symbol in symbols:
            result = self.scan_stock(symbol)
            if 'error' not in result and result.get('score', 0) >= min_score:
                results.append({
                    'symbol': symbol,
                    'score': result['score'],
                    'squeeze': result['squeeze']['squeeze_score'],
                    'recommendation': result['recommendation']['action'],
                    'risk': result['recommendation']['risk'],
                    'price': result['levels']['current'],
                    'target': result['levels']['target_1']
                })
        
        if results:
            df = pd.DataFrame(results)
            return df.sort_values('score', ascending=False)
        
        return pd.DataFrame()
