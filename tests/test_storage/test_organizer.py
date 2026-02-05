import json
import tempfile
from pathlib import Path

import pytest

from devon.storage.organizer import ModelStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage instance."""
    return ModelStorage(base_path=tmp_path / "models")


@pytest.fixture
def storage_with_model(temp_storage, tmp_path):
    """Create storage with a registered model."""
    # Create fake model files
    model_path = temp_storage.get_model_path("huggingface", "test/model")
    model_path.mkdir(parents=True, exist_ok=True)
    (model_path / "model.safetensors").write_bytes(b"x" * 1000)
    (model_path / "config.json").write_text('{"key": "value"}')

    temp_storage.register_model(
        source="huggingface",
        model_id="test/model",
        metadata={"model_name": "test-model", "author": "test"},
        files=["model.safetensors", "config.json"],
    )
    return temp_storage


class TestModelStorage:
    def test_init_creates_directory(self, tmp_path):
        storage = ModelStorage(base_path=tmp_path / "new_models")
        assert storage.base_path.exists()

    def test_get_model_path(self, temp_storage):
        path = temp_storage.get_model_path("huggingface", "Qwen/Qwen2.5")
        assert "huggingface" in str(path)
        assert "Qwen/Qwen2.5" in str(path)

    def test_register_and_list(self, storage_with_model):
        models = storage_with_model.list_local_models()
        assert len(models) == 1
        assert models[0]["model_id"] == "test/model"
        assert models[0]["source"] == "huggingface"

    def test_is_downloaded(self, storage_with_model):
        assert storage_with_model.is_downloaded("huggingface", "test/model")
        assert not storage_with_model.is_downloaded("huggingface", "other/model")

    def test_get_model_entry(self, storage_with_model):
        entry = storage_with_model.get_model_entry("huggingface", "test/model")
        assert entry is not None
        assert entry["model_id"] == "test/model"

    def test_get_model_entry_missing(self, temp_storage):
        entry = temp_storage.get_model_entry("huggingface", "missing/model")
        assert entry is None

    def test_delete_model(self, storage_with_model):
        result = storage_with_model.delete_model("huggingface", "test/model")
        assert result is True
        assert not storage_with_model.is_downloaded("huggingface", "test/model")
        assert len(storage_with_model.list_local_models()) == 0

    def test_delete_nonexistent(self, temp_storage):
        result = temp_storage.delete_model("huggingface", "missing/model")
        assert result is False

    def test_get_total_size(self, storage_with_model):
        total = storage_with_model.get_total_size()
        assert total > 0

    def test_list_filter_by_source(self, storage_with_model):
        models = storage_with_model.list_local_models(source="huggingface")
        assert len(models) == 1

        models = storage_with_model.list_local_models(source="ollama")
        assert len(models) == 0

    def test_index_persists(self, tmp_path):
        base = tmp_path / "models"

        # Create and register
        storage1 = ModelStorage(base_path=base)
        model_path = storage1.get_model_path("huggingface", "test/persist")
        model_path.mkdir(parents=True, exist_ok=True)
        (model_path / "model.bin").write_bytes(b"data")

        storage1.register_model(
            source="huggingface",
            model_id="test/persist",
            metadata={"name": "test"},
            files=["model.bin"],
        )

        # Reload and verify
        storage2 = ModelStorage(base_path=base)
        assert storage2.is_downloaded("huggingface", "test/persist")
