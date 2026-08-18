"""Historical breakout labeling and walk-forward evaluation utilities."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

from backend.analysis.liquidity_analysis import LiquidityAnalyzer
from .breakout_model import FEATURES, BreakoutProbabilityModel


class BreakoutBacktester:
    """Build labels without look-ahead leakage and evaluate a scanner."""

    def __init__(self, horizon: int = 10, target_return: float = 0.05) -> None:
        self.horizon = max(1, int(horizon))
        self.target_return = float(target_return)
        self.liquidity = LiquidityAnalyzer()

    def build_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create one feature row per historical date with a future-only label."""
        if df.empty:
            return pd.DataFrame(columns=FEATURES + ["label"])
        clean = df.copy()
        clean.columns = [str(c).capitalize() for c in clean.columns]
        required = {"High", "Low", "Close", "Volume"}
        if not required.issubset(clean.columns):
            raise ValueError("OHLCV columns are required")

        rows = []
        for i in range(30, len(clean) - self.horizon):
            history = clean.iloc[: i + 1]
            features = self.liquidity.analyze_liquidity(history)
            current = float(clean["Close"].iloc[i])
            future_high = float(clean["High"].iloc[i + 1 : i + 1 + self.horizon].max())
            label = int(future_high >= current * (1 + self.target_return))
            rows.append({**{key: features.get(key, 0.0) for key in FEATURES}, "label": label})
        return pd.DataFrame(rows)

    def evaluate(self, df: pd.DataFrame, threshold: float = 70.0) -> Dict[str, Any]:
        dataset = self.build_dataset(df)
        if len(dataset) < 50 or dataset["label"].nunique() < 2:
            return {"error": "بيانات تاريخية غير كافية للاختبار", "samples": len(dataset)}

        model = BreakoutProbabilityModel()
        metrics = model.fit(dataset[FEATURES], dataset["label"])
        probabilities = dataset[FEATURES].apply(
            lambda row: model.predict_probability(row.to_dict()), axis=1
        )
        signals = probabilities >= threshold
        labels = dataset["label"].to_numpy()
        predicted = signals.to_numpy(dtype=int)

        trades = int(signals.sum())
        wins = int(((predicted == 1) & (labels == 1)).sum())
        precision = wins / trades if trades else 0.0
        recall = wins / max(int(labels.sum()), 1)

        return {
            "samples": len(dataset),
            "signals": trades,
            "wins": wins,
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "accuracy": round(metrics.get("accuracy", 0.0) * 100, 2),
            "roc_auc": round(metrics.get("roc_auc", np.nan) * 100, 2),
            "threshold": threshold,
            "horizon_days": self.horizon,
            "target_return": self.target_return,
        }
