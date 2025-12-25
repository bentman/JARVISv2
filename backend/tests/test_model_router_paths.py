import os
import io
import wave
import tempfile
import hashlib
import types
import pytest

from app.services.model_router import ModelRouter
from app.core import config as config_module


def test_model_router_discovery_and_get_model_path(monkeypatch, tmp_path):
    # Arrange: create fake GGUF files
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    gguf_file = models_dir / "mistral-7b-instruct.gguf"
    gguf_file.write_bytes(b"fake-gguf-content")

    # Monkeypatch settings.MODEL_PATH to tmp
    original_model_path = config_module.settings.MODEL_PATH
    monkeypatch.setattr(config_module.settings, "MODEL_PATH", str(models_dir))

    # Avoid llama.cpp discovery/install
    monkeypatch.setattr(ModelRouter, "_find_llama_cpp", lambda self: "llama")

    try:
        # Act
        router = ModelRouter()
        # Assert: model path is absolute and matches the created file
        name = "mistral-7b-instruct"
        assert name in router.model_paths
        assert router.get_model_path(name) == str(gguf_file)
        # Hash present and correct
        assert name in router.model_hashes
        h = hashlib.sha256(b"fake-gguf-content").hexdigest()
        assert router.model_hashes[name] == h
    finally:
        # Restore settings
        monkeypatch.setattr(config_module.settings, "MODEL_PATH", original_model_path)
