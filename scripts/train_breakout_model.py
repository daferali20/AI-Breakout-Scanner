"""Train and persist the breakout model from one or more OHLCV CSV files.

Usage:
    python scripts/train_breakout_model.py data/*.csv

CSV files must contain Date, Open, High, Low, Close and Volume columns.
The script uses a chronological split through BreakoutProbabilityModel.fit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from backend.ml.backtest import BreakoutBacktester
from backend.ml.breakout_model import BreakoutProbabilityModel, FEATURES
from backend.ml.model_registry import ModelRegistry


def load_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame.columns = [str(c).capitalize() for c in frame.columns]
    required = {"High", "Low", "Close", "Volume"}
    if not required.issubset(frame.columns):
        raise ValueError(f"{path}: OHLCV columns are required")
    return frame.sort_values("Date" if "Date" in frame.columns else frame.index.name or frame.columns[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", default="models/breakout_model.joblib")
    parser.add_argument("--horizon", type=int, default=10)
    parser.add_argument("--target-return", type=float, default=0.05)
    args = parser.parse_args()

    builder = BreakoutBacktester(args.horizon, args.target_return)
    datasets = []
    for path in args.files:
        frame = load_csv(path)
        dataset = builder.build_dataset(frame)
        if not dataset.empty:
            datasets.append(dataset)

    if not datasets:
        raise SystemExit("No usable historical datasets were produced")

    dataset = pd.concat(datasets, ignore_index=True)
    model = BreakoutProbabilityModel()
    metrics = model.fit(dataset[FEATURES], dataset["label"])
    registry = ModelRegistry(args.output)
    saved = registry.save(model)

    print(f"samples={len(dataset)}")
    print(f"positive_rate={dataset['label'].mean():.4f}")
    print(f"accuracy={metrics.get('accuracy', 0):.4f}")
    print(f"roc_auc={metrics.get('roc_auc', float('nan')):.4f}")
    print(f"saved={saved}")


if __name__ == "__main__":
    main()
