"""Build a combined breakout dataset across multiple symbols with symbol-aware metadata."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from .dataset_builder import build_breakout_dataset


def build_multisymbol_dataset(
    symbol_frames: Mapping[str, pd.DataFrame],
    horizon: int = 10,
    target_return: float = 0.05,
    stop_return: float = -0.03,
) -> pd.DataFrame:
    datasets: list[pd.DataFrame] = []
    for symbol, frame in symbol_frames.items():
        if frame is None or frame.empty:
            continue
        dataset = build_breakout_dataset(frame, horizon, target_return, stop_return)
        if dataset.empty:
            continue
        dataset.insert(0, "symbol", symbol)
        datasets.append(dataset)
    if not datasets:
        return pd.DataFrame()
    return pd.concat(datasets, ignore_index=True)


def chronological_symbol_split(
    dataset: pd.DataFrame,
    test_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split chronologically using a timestamp column when available."""
    data = dataset.copy()
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data = data.sort_values("Date")
    else:
        data = data.sort_index()
    split = max(1, int(len(data) * (1 - test_fraction)))
    return data.iloc[:split].reset_index(drop=True), data.iloc[split:].reset_index(drop=True)
