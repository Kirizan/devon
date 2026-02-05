import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ModelStorage:
    """Manage local model storage."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize storage manager.

        Default: ~/.cache/devon/models/
        """
        if base_path is None:
            base_path = Path.home() / ".cache" / "devon" / "models"

        self.base_path = Path(base_path)
        self.index_file = self.base_path.parent / "index.json"

        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()

    def get_model_path(self, source: str, model_id: str) -> Path:
        """Get storage path for a model."""
        return self.base_path / source / model_id

    def register_model(
        self,
        source: str,
        model_id: str,
        metadata: Dict,
        files: List[str],
    ) -> None:
        """Register downloaded model."""
        path = self.get_model_path(source, model_id)
        size_bytes = sum(
            (path / f).stat().st_size for f in files if (path / f).exists()
        )

        # Remove non-serializable data from metadata
        clean_metadata = {}
        for k, v in metadata.items():
            if k == "extra":
                continue
            try:
                json.dumps(v)
                clean_metadata[k] = v
            except (TypeError, ValueError):
                clean_metadata[k] = str(v)

        entry = {
            "source": source,
            "model_id": model_id,
            "path": str(path),
            "metadata": clean_metadata,
            "files": files,
            "downloaded_at": datetime.now().isoformat(),
            "last_used": None,
            "size_bytes": size_bytes,
        }

        key = f"{source}::{model_id}"
        self.index[key] = entry
        self._save_index()

    def list_local_models(self, source: Optional[str] = None) -> List[Dict]:
        """List all locally downloaded models."""
        models = []
        for entry in self.index.values():
            if source is None or entry["source"] == source:
                models.append(entry)
        return models

    def is_downloaded(self, source: str, model_id: str) -> bool:
        """Check if model is downloaded."""
        return f"{source}::{model_id}" in self.index

    def get_model_entry(self, source: str, model_id: str) -> Optional[Dict]:
        """Get entry for a model."""
        return self.index.get(f"{source}::{model_id}")

    def delete_model(self, source: str, model_id: str) -> bool:
        """Delete model from disk and index."""
        key = f"{source}::{model_id}"
        if key not in self.index:
            return False

        path = Path(self.index[key]["path"])
        if path.exists():
            shutil.rmtree(path)

        del self.index[key]
        self._save_index()
        return True

    def get_total_size(self) -> int:
        """Get total size of all models."""
        return sum(entry["size_bytes"] for entry in self.index.values())

    def mark_used(self, source: str, model_id: str) -> None:
        """Mark a model as recently used."""
        key = f"{source}::{model_id}"
        if key in self.index:
            self.index[key]["last_used"] = datetime.now().isoformat()
            self._save_index()

    def _load_index(self) -> Dict:
        """Load index from disk."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {}

    def _save_index(self) -> None:
        """Save index to disk."""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)
