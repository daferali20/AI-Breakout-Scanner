import pandas as pd

from backend.market.regime import detect_market_regime


def test_market_regime_returns_expected_schema():
    n = 100
    close = pd.Series([100 + i * 0.5 for i in range(n)])
    frame = pd.DataFrame({"Close": close})
    result = detect_market_regime(frame)
    assert result["regime"] in {"Bull", "Bear", "High Volatility", "Sideways", "Insufficient Data", "Unknown"}
    assert 0 <= result["trend_score"] <= 100
    assert result["risk_multiplier"] > 0
