import pandas as pd

from backend.analysis.breakout_features import extract_breakout_features


def test_extract_breakout_features_returns_finite_values():
    n = 80
    frame = pd.DataFrame({
        "Open": [100 + i * 0.2 for i in range(n)],
        "High": [101 + i * 0.2 for i in range(n)],
        "Low": [99 + i * 0.2 for i in range(n)],
        "Close": [100 + i * 0.2 for i in range(n)],
        "Volume": [1_000_000 + i * 5_000 for i in range(n)],
    })
    result = extract_breakout_features(frame)
    assert result
    assert all(pd.notna(v) for v in result.values())
    assert result["relative_volume"] > 0
    assert 0 <= result["price_position"] <= 1
    assert 0 <= result["smart_money_score"] <= 100
