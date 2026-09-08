"""Model Registry integration boundary.

Provides the interface to dynamically load the active ML models
(e.g., StateEstimator weights) without requiring a deployment.
"""

from typing import Protocol


class ModelRegistry(Protocol):
    """Interface for retrieving ML models and configuration."""

    async def get_active_model_version(self, model_name: str) -> str:
        """Get the active version string for a model."""
        ...

    async def get_model_weights(self, model_name: str, version: str) -> bytes:
        """Download model weights."""
        ...


class MLflowRegistryAdapter(ModelRegistry):
    """Adapter for MLflow (placeholder for actual implementation)."""

    async def get_active_model_version(self, model_name: str) -> str:
        return "1.0.0"

    async def get_model_weights(self, model_name: str, version: str) -> bytes:
        return b"dummy_weights"
