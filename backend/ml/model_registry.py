"""Small model registry for loading/saving the breakout classifier safely."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib

from .breakout_model import BreakoutProbabilityModel


class ModelRegistry:
    """Persist a trained breakout model without breaking cold starts."""

    def __init__(self, path: str = "models/breakout_model.joblib") -> None:
        self.path = Path(path)

    def save(self, model: BreakoutProbabilityModel) -> str:
        if not model.fitted or model.model is None:
            raise ValueError("Cannot save an unfitted breakout model")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": model.model,
                "metrics": model.metrics,
                "feature_names": model.feature_names,
            },
            self.path,
        )
        return str(self.path)

    def load(self) -> Optional[BreakoutProbabilityModel]:
        if not self.path.exists():
            return None
        payload = joblib.load(self.path)
        model = BreakoutProbabilityModel()
        model.model = payload.get("model")
        model.metrics = payload.get("metrics", {})
        model.fitted = model.model is not None
        return model if model.fitted else None
