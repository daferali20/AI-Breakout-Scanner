import pandas as pd

from backend.ml.multisymbol_dataset import build_multisymbol_dataset, chronological_symbol_split


def _frame(n=40):
    return pd.DataFrame({
        "Open": [100 + i for i in range(n)],
        "High": [101 + i for i in range(n)],
        "Low": [99 + i for i in range(n)],
        "Close": [100 + i for i in range(n)],
        "Volume": [1_000_000] * n,
    })


def test_multisymbol_dataset_preserves_symbols():
    result = build_multisymbol_dataset({"AAA": _frame(), "BBB": _frame()})
    assert set(result["symbol"]) == {"AAA", "BBB"}
    assert len(result) == 70


def test_split_is_chronological():
    data = pd.DataFrame({"Date": pd.date_range("2026-01-01", periods=10), "label": range(10)})
    train, test = chronological_symbol_split(data, 0.2)
    assert train["Date"].max() < test["Date"].min()
