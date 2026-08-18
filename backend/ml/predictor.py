"""Production-facing breakout predictor with transparent model status."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .breakout_model import BreakoutProbabilityModel
from .model_registry import ModelRegistry


class BreakoutPredictor:
    def __init__(self, model_path: str = "models/breakout_model.joblib") -> None:
        self.registry = ModelRegistry(model_path)
        self.model: Optional[BreakoutProbabilityModel] = self.registry.load()

    @property
    def trained(self) -> bool:
        return bool(self.model and self.model.fitted)

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        model = self.model or BreakoutProbabilityModel()
        return model.predict(features)
