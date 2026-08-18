import pandas as pd

from backend.ranking.opportunity_ranker import rank_opportunities


def test_ranker_orders_by_weighted_opportunity_score():
    rows = [
        {"symbol": "AAA", "breakout_probability": 90, "setup_score": 90, "liquidity_score": 90, "momentum_score": 90, "trend_score": 90, "false_breakout_risk": 10},
        {"symbol": "BBB", "breakout_probability": 60, "setup_score": 60, "liquidity_score": 60, "momentum_score": 60, "trend_score": 60, "false_breakout_risk": 40},
    ]
    result = rank_opportunities(rows)
    assert result.iloc[0]["symbol"] == "AAA"
    assert result.iloc[0]["opportunity_score"] > result.iloc[1]["opportunity_score"]
    assert result.iloc[0]["signal_quality"] == "Elite"
