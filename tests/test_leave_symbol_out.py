import pandas as pd

from backend.ml.breakout_model import FEATURES
from backend.ml.leave_symbol_out import leave_symbols_out


def test_leave_symbol_out_requires_symbol_column():
    frame = pd.DataFrame({feature: [0.5] * 10 for feature in FEATURES})
    frame["label"] = [0, 1] * 5
    try:
        leave_symbols_out(frame, ["AAA"])
    except ValueError as exc:
        assert "symbol" in str(exc)
    else:
        raise AssertionError("Expected missing symbol column to fail")
