# backend/ai/predictor.py
"""
نموذج الذكاء الاصطناعي للتنبؤ بالانفجارات السعرية
"""

import pandas as pd
import numpy as np
from typing import Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AIPredictor:
    """التنبؤ بالانفجارات السعرية باستخدام Random Forest"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.features = [
            'squeeze_score', 'volatility_score', 'compression_score',
            'volume_ratio', 'rsi', 'price_position', 'bb_width'
        ]
        self._train_synthetic()
    
    def _train_synthetic(self):
        """تدريب النموذج على بيانات محاكاة"""
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.randn(n_samples, len(self.features))
        y = np.zeros(n_samples)
        
        for i in range(n_samples):
            squeeze = X[i, 0] > 0.5
            volatility = X[i, 1] > 0.5
            compression = X[i, 2] > 0.5
            volume = X[i, 3] > 0.6
            rsi = 0.3 < X[i, 4] < 0.7
            
            if squeeze and volatility and compression and volume and rsi:
                y[i] = 1
            elif np.random.random() > 0.85:
                y[i] = 1
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, indicators: Dict) -> Dict:
        """التنبؤ بالانفجار"""
        try:
            features = self._extract_features(indicators)
            if features is None:
                return self._fallback_prediction(indicators)
            
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            prob = self.model.predict_proba(features_scaled)[0][1] * 100
            
            return {
                'probability': round(prob, 2),
                'prediction': 'explosive' if prob > 55 else 'normal',
                'confidence': self._calculate_confidence(indicators)
            }
            
        except Exception:
            return self._fallback_prediction(indicators)
    
    def _extract_features(self, indicators: Dict) -> np.ndarray:
        try:
            features = [
                indicators.get('squeeze_score', 50) / 100,
                indicators.get('volatility_score', 50) / 100,
                indicators.get('compression_score', 50) / 100,
                min(indicators.get('volume_ratio', 1) / 5, 1),
                indicators.get('rsi', 50) / 100,
                indicators.get('price_position', 50) / 100,
                min(indicators.get('bb_width', 0.1) * 10, 1)
            ]
            return np.array(features)
        except:
            return None
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        factors = [
            indicators.get('squeeze_score', 0),
            indicators.get('volume_ratio', 0) * 40,
            indicators.get('compression_score', 0)
        ]
        return min(100, max(0, sum(factors) / len(factors)))
    
    def _fallback_prediction(self, indicators: Dict) -> Dict:
        squeeze = indicators.get('squeeze_score', 0)
        volume = indicators.get('volume_ratio', 1)
        prob = min(100, (squeeze * 0.6 + volume * 20))
        
        return {
            'probability': round(prob, 2),
            'prediction': 'explosive' if prob > 55 else 'normal',
            'confidence': min(100, squeeze * 0.6 + 20)
        }
