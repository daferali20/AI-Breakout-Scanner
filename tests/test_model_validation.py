import pandas as pd

from backend.ml.breakout_model import FEATURES
from backend.ml.model_validation import walk_forward_validate


def test_walk_forward_requires_enough_history():
    frame = pd.DataFrame({feature: [0.5] * 30 for feature in FEATURES})
    frame["label"] = [0, 1] * 15
    result = walk_forward_validate(frame, min_train=20, test_size=10)
    assert result["folds"] == 0
