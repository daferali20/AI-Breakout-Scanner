"""Out-of-symbol evaluation: train on some symbols and test on unseen symbols."""

from __future__ import annotations

import pandas as pd

from .backtest_report import build_performance_report, calibration_table
from .breakout_model import BreakoutProbabilityModel, FEATURES


def leave_symbols_out(dataset: pd.DataFrame, test_symbols: list[str]) -> dict:
    data = dataset.dropna(subset=FEATURES + ["label"]).copy()
    if "symbol" not in data.columns:
        raise ValueError("Dataset must contain a symbol column")
    test_set = set(test_symbols)
    train = data[~data["symbol"].isin(test_set)]
    test = data[data["symbol"].isin(test_set)]
    if train.empty or test.empty:
        return {"trained": False, "train_symbols": sorted(train["symbol"].unique()), "test_symbols": sorted(test["symbol"].unique())}
    model = BreakoutProbabilityModel()
    model.fit(train[FEATURES], train["label"])
    probabilities = []
    outcomes = []
    returns = []
    for _, row in test.iterrows():
        result = model.predict(row[FEATURES].to_dict())
        probabilities.append(result["breakout_probability"])
        outcomes.append(int(row["label"]))
        returns.append(float(row.get("forward_return", 0.0)))
    return {
        "trained": True,
        "train_symbols": sorted(train["symbol"].unique()),
        "test_symbols": sorted(test["symbol"].unique()),
        "model_metrics": model.metrics,
        "performance": build_performance_report(pd.Series(returns)),
        "calibration": calibration_table(pd.Series(probabilities), pd.Series(outcomes)),
    }
