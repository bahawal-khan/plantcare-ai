"""Loads the trained EfficientNetB0 classifier once and holds it in memory.

Per ARCHITECTURE.md ("Model is loaded once, not per request") and CLAUDE.md
rule 9, ``ModelService.load`` is called exactly once, from the FastAPI
lifespan in ``app/main.py``, and the resulting instance is reused for every
request via ``app.state.model_service``. This module only wraps the existing
Phase 03-06 model/preprocessing modules (``ml/src/models/efficientnet.py``,
``ml/src/data/class_mapping.py``) and the Phase 07 Grad-CAM target layer --
it does not retrain or redefine the model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tensorflow import keras

from ..core.config import Settings
from ..core.errors import ModelUnavailableError
from ml.src.data.class_mapping import load_class_mapping
from ml.src.explainability.gradcam import TARGET_LAYER_NAME
from ml.src.models.efficientnet import load_model


@dataclass(frozen=True)
class ModelService:
    """Immutable holder for the loaded model and its metadata."""

    model: keras.Model
    class_names: list[str]
    model_path: Path
    image_size: tuple[int, int]
    target_layer: str
    evaluation_metrics: dict | None

    @property
    def num_classes(self) -> int:
        return len(self.class_names)

    def predict_probabilities(self, image_batch) -> "object":
        """Run a forward pass on one preprocessed ``(1, H, W, 3)`` batch."""
        return self.model.predict(image_batch, verbose=0)[0]

    @classmethod
    def load(cls, settings: Settings) -> "ModelService":
        model_path = Path(settings.model_path)
        if not model_path.is_file():
            raise ModelUnavailableError(f"Model artifact not found at {model_path}")

        mapping_path = Path(settings.class_mapping_path)
        if not mapping_path.is_file():
            raise ModelUnavailableError(f"Class mapping not found at {mapping_path}")

        try:
            model = load_model(model_path)
        except Exception as exc:  # pragma: no cover - defensive, exercised via missing-file path
            raise ModelUnavailableError(f"Failed to load model from {model_path}: {exc}") from exc

        class_mapping = load_class_mapping(mapping_path)
        class_names = [name for name, _ in sorted(class_mapping.items(), key=lambda kv: kv[1])]
        if not class_names:
            raise ModelUnavailableError(f"Class mapping at {mapping_path} is empty")

        # (H, W) recovered from the model's own input layer, rather than a
        # separately configured constant, so this stays correct for any
        # checkpoint (including the small fixtures used in tests).
        input_shape = model.input_shape
        image_size = (int(input_shape[1]), int(input_shape[2]))

        evaluation_metrics: dict | None = None
        metrics_path = Path(settings.evaluation_metrics_path)
        if metrics_path.is_file():
            evaluation_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

        return cls(
            model=model,
            class_names=class_names,
            model_path=model_path,
            image_size=image_size,
            target_layer=TARGET_LAYER_NAME,
            evaluation_metrics=evaluation_metrics,
        )
