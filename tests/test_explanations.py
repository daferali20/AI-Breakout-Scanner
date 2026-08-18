from backend.ranking.explanations import explain_opportunity


def test_explanation_contains_dominant_signals():
    reasons = explain_opportunity({
        "breakout_probability": 90,
        "liquidity_score": 90,
        "momentum_score": 85,
        "trend_score": 88,
        "false_breakout_risk": 10,
        "relative_volume": 2.5,
    })
    assert "High ML breakout probability" in reasons
    assert "Strong liquidity" in reasons
    assert "High relative volume" in reasons
    assert "Low false-breakout risk" in reasons
