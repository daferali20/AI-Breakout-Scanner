import pandas as pd

from backend.ml.dataset_builder import build_breakout_dataset


def test_dataset_contains_forward_outcomes_without_future_feature_leak():
    n = 40
    frame = pd.DataFrame({
        "Open": [100.0 + i for i in range(n)],
        "High": [101.0 + i for i in range(n)],
        "Low": [99.0 + i for i in range(n)],
        "Close": [100.0 + i for i in range(n)],
        "Volume": [1_000_000.0] * n,
    })
    result = build_breakout_dataset(frame, horizon=5, target_return=0.01)
    assert len(result) == n - 5
    assert {"label", "forward_return", "mfe", "mae", "holding_horizon"}.issubset(result.columns)
    assert result["holding_horizon"].eq(5).all()
