"""Immutable filesystem model registry with checksummed, evaluated artifacts."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any


class FileModelRegistry:
    def __init__(self, root: str | Path = "models") -> None:
        self.root = Path(root)

    def directory(self, model_name: str, version: str) -> Path:
        if not all(re.fullmatch(r"[A-Za-z0-9_-]+", value) for value in (model_name, version)):
            raise ValueError("Invalid model identity")
        return self.root / model_name / version

    def register(self, model_name: str, version: str, source: str | Path, metadata: dict[str, Any]) -> Path:
        required = {"training_date", "evaluation_metrics", "feature_names", "safety_constraints_met"}
        if not required <= metadata.keys() or metadata["safety_constraints_met"] is not True:
            raise ValueError("Model promotion requires passing safety evaluation")
        data = Path(source).read_bytes()
        directory = self.directory(model_name, version)
        directory.mkdir(parents=True, exist_ok=False)
        artifact = directory / "model.lgb"
        artifact.write_bytes(data)
        (directory / "metadata.json").write_text(json.dumps({**metadata, "sha256": hashlib.sha256(data).hexdigest()}))
        return artifact

    def load(self, model_name: str, version: str) -> tuple[Path, dict[str, Any]]:
        directory = self.directory(model_name, version)
        metadata = json.loads((directory / "metadata.json").read_text())
        artifact = directory / "model.lgb"
        if metadata["safety_constraints_met"] is not True or hashlib.sha256(artifact.read_bytes()).hexdigest() != metadata["sha256"]:
            raise ValueError("Untrusted model artifact")
        return artifact, metadata
