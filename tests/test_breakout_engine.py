import unittest

import numpy as np
import pandas as pd

from backend.analysis.indicators import TechnicalIndicators
from backend.analysis.liquidity_analysis import LiquidityAnalyzer
from backend.scanner.breakout_scanner import BreakoutScanner


class BreakoutEngineTests(unittest.TestCase):
    @staticmethod
    def make_data(rows: int = 260) -> pd.DataFrame:
        rng = np.random.default_rng(42)
        returns = rng.normal(0.0008, 0.012, rows)
        close = 20 * np.exp(np.cumsum(returns))
        close[-5:] *= np.linspace(1.0, 1.10, 5)
        high = close * (1 + rng.uniform(0.002, 0.015, rows))
        low = close * (1 - rng.uniform(0.002, 0.015, rows))
        open_ = close * (1 + rng.normal(0, 0.003, rows))
        volume = rng.integers(500_000, 1_000_000, rows).astype(float)
        volume[-1] *= 3
        return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume})

    def test_indicators_return_breakout_features(self):
        data = self.make_data()
        result = TechnicalIndicators().calculate_all(data)
        for key in ("relative_volume", "resistance_distance", "breakout_score", "trend_strength"):
            self.assertIn(key, result)
        self.assertTrue(0 <= result["breakout_score"] <= 100)

    def test_liquidity_is_data_driven(self):
        data = self.make_data()
        result = LiquidityAnalyzer().analyze_liquidity(data)
        self.assertNotEqual(result["smart_money_flow"], 0.68)
        self.assertNotEqual(result["volume_trend"], 2.4)
        self.assertTrue(0 <= result["smart_money_score"] <= 100)

    def test_scanner_returns_structured_result(self):
        data = self.make_data()
        result = BreakoutScanner().scan_stock("TEST", data)
        self.assertNotIn("error", result)
        self.assertIn(result["phase"], {"WATCH", "BUILDING", "BREAKOUT_READY", "BREAKOUT_CONFIRMED"})
        self.assertTrue(0 <= result["score"] <= 100)
        self.assertTrue(0 <= result["breakout_probability"] <= 100)
        self.assertTrue(0 <= result["false_breakout_risk"] <= 100)

    def test_market_scan_empty_is_safe(self):
        result = BreakoutScanner().scan_market([])
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()
