"""
PriceNest — Model Artifact Loader (Inference Subsystem)
Safe deserialization, schema validation, and lifespan memory caching (SRS FR-08).
"""

import logging
from pathlib import Path
from typing import Any, Optional

import joblib

from ml.common.constants import DEFAULT_MODEL_FILENAME, DEFAULT_MODEL_VERSION

logger = logging.getLogger("pricenest.ml.loader")


class ModelLoader:
    """Manages discovery, verification, and deserialization of fitted ML pipeline artifacts."""

    def __init__(self, artifact_filename: str = DEFAULT_MODEL_FILENAME):
        self.artifact_filename = artifact_filename
        self.cached_pipeline: Optional[Any] = None
        self.resolved_path: Optional[Path] = None
        self.version: str = DEFAULT_MODEL_VERSION

    def resolve_artifact_path(self, custom_path: Optional[Path] = None) -> Path:
        """Resolve absolute path to model artifact across standard repository locations."""
        if custom_path and Path(custom_path).exists():
            return Path(custom_path).resolve()

        # Potential locations relative to project root
        candidate_paths = [
            Path("ml/inference/artifacts") / self.artifact_filename,
            Path("ml/models") / self.artifact_filename,
            Path(__file__).resolve().parent.parent / "artifacts" / self.artifact_filename,
            Path(__file__).resolve().parent.parent.parent / "models" / self.artifact_filename,
        ]

        for p in candidate_paths:
            if p.exists():
                return p.resolve()

        # Fallback to direct path
        return Path("ml/inference/artifacts") / self.artifact_filename

    def load(self, custom_path: Optional[Path] = None) -> Any:
        """Load and validate the scikit-learn pipeline artifact."""
        target_path = self.resolve_artifact_path(custom_path)
        self.resolved_path = target_path

        if not target_path.exists():
            logger.error(f"Model artifact not found at {target_path}")
            raise FileNotFoundError(f"ML model artifact not found at: {target_path}")

        try:
            logger.info(f"Loading serialized ML pipeline from {target_path}...")
            pipeline = joblib.load(target_path)
            self._validate_pipeline(pipeline)
            self.cached_pipeline = pipeline
            logger.info("ML pipeline loaded and verified successfully.")
            return pipeline
        except Exception as e:
            logger.error(f"Failed to load artifact from {target_path}: {e}", exc_info=True)
            self.cached_pipeline = None
            raise

    def is_loaded(self) -> bool:
        return self.cached_pipeline is not None

    def get_pipeline(self) -> Any:
        if self.cached_pipeline is None:
            return self.load()
        return self.cached_pipeline

    def _validate_pipeline(self, pipeline: Any) -> None:
        """Validate that the loaded object is a valid scikit-learn Pipeline with preprocessor and regressor."""
        if not hasattr(pipeline, "named_steps"):
            raise ValueError("Loaded artifact is not a valid scikit-learn Pipeline with named_steps.")
        if "preprocessor" not in pipeline.named_steps:
            raise ValueError("Pipeline missing required 'preprocessor' step.")
        if "regressor" not in pipeline.named_steps:
            raise ValueError("Pipeline missing required 'regressor' step.")


model_loader = ModelLoader()
