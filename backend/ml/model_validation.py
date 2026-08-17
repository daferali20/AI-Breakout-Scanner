"""Walk-forward validation for breakout probability models."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .breakout_model import BreakoutProbabilityModel, FEATURES
from .backtest_report import build_performance_report, calibration_table


def walk_forward_validate(dataset: pd.DataFrame, min_train: int = 100, test_size: int = 25) -> dict:
    data = dataset.dropna(subset=FEATURES + ["label"]).reset_index(drop=True)
    folds = []
    probabilities = []
    outcomes = []
    returns = []

    if len(data) < min_train + test_size:
        return {"folds": 0, "performance": build_performance_report(pd.Series(dtype=float)), "calibration": calibration_table(pd.Series(dtype=float), pd.Series(dtype=float))}

    for end in range(min_train, len(data), test_size):
        test = data.iloc[end:min(end + test_size, len(data))]
        if test.empty:
            break
        train = data.iloc[:end]
        model = BreakoutProbabilityModel()
        try:
            model.fit(train[FEATURES], train["label"])
        except ValueError:
            continue
        for _, row in test.iterrows():
            result = model.predict(row[FEATURES].to_dict())
            probabilities.append(result["breakout_probability"])
            outcomes.append(int(row["label"]))
            returns.append(float(row.get("forward_return", 0.0)))
        folds.append({"train_rows": len(train), "test_rows": len(test)})

    return {
        "folds": len(folds),
        "performance": build_performance_report(pd.Series(returns)),
        "calibration": calibration_table(pd.Series(probabilities), pd.Series(outcomes)),
    }
