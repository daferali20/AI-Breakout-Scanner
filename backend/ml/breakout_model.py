"""Trainable breakout-probability model with a safe rule-based fallback."""

from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np
import pandas as pd

FEATURES = [
    "rsi", "relative_volume", "volume_trend", "smart_money_score",
    "trend_strength", "price_position", "resistance_distance",
    "resistance_break", "bollinger_width", "atr_ratio", "price_change",
    "price_momentum", "compression_level",
]


class BreakoutProbabilityModel:
    def __init__(self) -> None:
        self.model: Any = None
        self.fitted = False
        self.metrics: Dict[str, float] = {}

    @property
    def feature_names(self) -> list[str]:
        return FEATURES.copy()

    def fit(self, X: pd.DataFrame, y: Iterable[int]) -> Dict[str, float]:
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score

        frame = self._prepare(X)
        target = pd.Series(list(y), index=frame.index).astype(int)
        if len(frame) < 50 or target.nunique() < 2:
            raise ValueError("At least 50 labeled rows with both classes are required")
        split = max(int(len(frame) * 0.8), 1)
        split = min(split, len(frame) - 1)
        train_x, test_x = frame.iloc[:split], frame.iloc[split:]
        train_y, test_y = target.iloc[:split], target.iloc[split:]
        self.model = HistGradientBoostingClassifier(
            max_iter=180, learning_rate=0.05, max_leaf_nodes=15,
            l2_regularization=1.0, random_state=42,
        )
        self.model.fit(train_x, train_y)
        self.fitted = True
        probability = self.model.predict_proba(test_x)[:, 1]
        prediction = (probability >= 0.5).astype(int)
        metrics = {"accuracy": float(accuracy_score(test_y, prediction))}
        metrics["roc_auc"] = float(roc_auc_score(test_y, probability)) if test_y.nunique() == 2 else float("nan")
        self.metrics = metrics
        return metrics

    def predict_probability(self, data: Dict[str, Any] | pd.DataFrame) -> float:
        frame = self._prepare(pd.DataFrame([data]) if isinstance(data, dict) else data)
        if self.fitted and self.model is not None:
            return float(np.clip(self.model.predict_proba(frame)[0, 1] * 100, 0, 100))
        return self._fallback_probability(frame.iloc[0].to_dict())

    def predict(self, data: Dict[str, Any] | pd.DataFrame) -> Dict[str, Any]:
        probability = self.predict_probability(data)
        return {
            "breakout_probability": round(probability, 2),
            "model_type": "hist_gradient_boosting" if self.fitted else "rule_based_baseline",
            "trained": self.fitted,
            "metrics": self.metrics.copy(),
        }

    @staticmethod
    def _prepare(frame: pd.DataFrame) -> pd.DataFrame:
        result = frame.copy()
        for feature in FEATURES:
            result[feature] = pd.to_numeric(result.get(feature, 0.0), errors="coerce")
        return result[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    @staticmethod
    def _fallback_probability(row: Dict[str, Any]) -> float:
        score = 45.0
        score += np.clip(row.get("relative_volume", 1.0) - 1.0, 0, 3) * 8
        score += np.clip(row.get("smart_money_score", 50.0) - 50, -50, 50) * 0.22
        score += np.clip(row.get("trend_strength", 0.5) - 0.5, -0.5, 0.5) * 35
        score += np.clip(row.get("price_position", 0.5) - 0.5, -0.5, 0.5) * 20
        score += np.clip(row.get("resistance_break", 1.0) - 1.0, 0, 0.1) * 180
        score += np.clip(row.get("compression_level", 0.0), 0, 1) * 10
        rsi = row.get("rsi", 50.0)
        if 50 <= rsi <= 72:
            score += 8
        elif rsi > 80 or rsi < 35:
            score -= 8
        return float(np.clip(score, 0, 100))
