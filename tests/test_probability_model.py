import numpy as np
import pandas as pd

from backend.ml.breakout_model import BreakoutProbabilityModel, FEATURES


def _frame(rows=80):
    rng = np.random.default_rng(42)
    data = {name: rng.normal(0.5, 0.1, rows) for name in FEATURES}
    data["rsi"] = rng.uniform(40, 75, rows)
    data["relative_volume"] = rng.uniform(0.7, 3.0, rows)
    data["smart_money_score"] = rng.uniform(20, 90, rows)
    return pd.DataFrame(data)


def test_fallback_probability_is_bounded():
    model = BreakoutProbabilityModel()
    result = model.predict({"rsi": 65, "relative_volume": 2.5, "smart_money_score": 80})
    assert 0 <= result["breakout_probability"] <= 100
    assert result["trained"] is False


def test_model_can_train():
    frame = _frame()
    target = (frame["relative_volume"] > 1.7).astype(int)
    model = BreakoutProbabilityModel()
    metrics = model.fit(frame, target)
    assert model.fitted is True
    assert "accuracy" in metrics
    assert 0 <= model.predict_probability(frame.iloc[0].to_dict()) <= 100
