import pandas as pd

from backend.ml.backtest_report import build_performance_report, calibration_table


def test_performance_report():
    report = build_performance_report(pd.Series([0.10, -0.05, 0.03]))
    assert report["signals"] == 3
    assert report["wins"] == 2
    assert report["losses"] == 1
    assert report["win_rate"] > 60
    assert report["max_drawdown"] < 0


def test_calibration_table():
    table = calibration_table(pd.Series([10, 20, 80, 90]), pd.Series([0, 0, 1, 1]))
    assert not table.empty
    assert {"samples", "predicted_probability", "actual_rate"}.issubset(table.columns)
