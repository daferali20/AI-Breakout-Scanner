# backend/scanner/breakout_scanner.py

import os
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

# إضافة المسار لتجنب مشاكل الاستيراد
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد من التحليل
from analysis.indicators import TechnicalIndicators
from analysis.squeeze_detector import SqueezeDetector


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
                return {"error": f"لا يمكن جلب بيانات السهم {symbol}"}

        if df.empty or len(df) < 50:
            return {"error": f"بيانات غير كافية للسهم {symbol}"}

        try:
            # 1. تحليل الانضغاط
            squeeze_result = self.squeeze.detect(df)
            if "error" in squeeze_result:
                return squeeze_result

            # 2. المؤشرات الفنية
            indicators = self.indicators.calculate_all(df)

            # 3. دمج النتائج
            all_indicators = {
                **squeeze_result,
                **indicators,
                "current_price": df["Close"].iloc[-1],
            }

            # 4. حساب الدرجة النهائية
            total_score = self._calculate_score(all_indicators)

            # 5. مستويات التداول
            levels = self._calculate_levels(df)

            return {
                "symbol": symbol,
                "score": total_score,
                "squeeze": squeeze_result,
                "indicators": indicators,
                "levels": levels,
                "recommendation": self._get_recommendation(total_score),
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_score(self, indicators: Dict) -> float:
        """حساب الدرجة النهائية"""
        squeeze_score = indicators.get("squeeze_score", 50)
        volatility_score = indicators.get("volatility_score", 50)
        volume_score = indicators.get("volume_score", 50)
        rsi_score = indicators.get("rsi_score", 50)
        price_position = indicators.get("price_position", 50)

        weights = {
            "squeeze": 0.40,
            "volatility": 0.15,
            "volume": 0.20,
            "rsi": 0.15,
            "price": 0.10,
        }

        score = (
            squeeze_score * weights["squeeze"]
            + volatility_score * weights["volatility"]
            + volume_score * weights["volume"]
            + rsi_score * weights["rsi"]
            + price_position * weights["price"]
        )

        return round(min(100, max(0, score)), 2)

    def _calculate_levels(self, df: pd.DataFrame) -> Dict:
        """حساب مستويات التداول"""
        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        current = close.iloc[-1]
        atr = (high - low).rolling(14).mean().iloc[-1] or current * 0.02
        resistance = high.iloc[-20:].max()
        support = low.iloc[-20:].min()

        return {
            "current": round(current, 2),
            "entry": round(resistance + (atr * 0.5), 2),
            "stop_loss": round(current - (atr * 1.5), 2),
            "target_1": round(current + (atr * 2), 2),
            "target_2": round(current + (atr * 3.5), 2),
        }

    def _get_recommendation(self, score: float) -> Dict:
        """توليد التوصية"""
        if score >= 75:
            return {"action": "🟢 شراء قوي", "risk": "منخفض"}
        elif score >= 60:
            return {"action": "🟡 شراء", "risk": "متوسط"}
        elif score >= 45:
            return {"action": "🔍 مراقبة", "risk": "متوسط"}
        else:
            return {"action": "🔴 تجنب", "risk": "مرتفع"}

    def scan_symbols(
        self, symbols: List[str], min_score: float = 0
    ) -> List[Dict]:
        """الدالة المطلوبة من واجهة المستخدم لاستقبال مصفوفة الأسهم والإرجاع كـ List أو DataFrame"""
        results = []

        for symbol in symbols:
            result = self.scan_stock(symbol)
            if "error" not in result and result.get("score", 0) >= min_score:
                results.append(
                    {
                        "symbol": symbol,
                        "score": result["score"],
                        "squeeze": result["squeeze"].get("squeeze_score", 0),
                        "is_squeeze": result["squeeze"].get(
                            "is_squeeze", False
                        ),
                        "recommendation": result["recommendation"]["action"],
                        "risk": result["recommendation"]["risk"],
                        "price": result["levels"]["current"],
                        "target": result["levels"]["target_1"],
                    }
                )

        return results

    def scan_market(
        self, symbols: List[str], min_score: float = 60
    ) -> pd.DataFrame:
        """مسح السوق وإعادة النتائج كـ DataFrame"""
        results = self.scan_symbols(symbols, min_score=min_score)

        if results:
            df = pd.DataFrame(results)
            return df.sort_values("score", ascending=False)

        return pd.DataFrame()
