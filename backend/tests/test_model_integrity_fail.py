import hashlib
from app.services.model_router import ModelRouter
from app.core import config as config_module
import pytest


def test_model_integrity_failure_raises(monkeypatch, tmp_path):
    # Create a GGUF file and instantiate router to compute initial hash
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    file_path = models_dir / "llama-3.2-3b.gguf"
    file_path.write_bytes(b"original")

    original_model_path = config_module.settings.MODEL_PATH
    monkeypatch.setattr(config_module.settings, "MODEL_PATH", str(models_dir))
    # Avoid actual llama.cpp
    monkeypatch.setattr(ModelRouter, "_find_llama_cpp", lambda self: "llama")
    # Prevent running inference if integrity passes by mistake
    monkeypatch.setattr(ModelRouter, "_run_llama_inference", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("should not run")))

    try:
        router = ModelRouter()
        # Tamper with the file to change its hash
        file_path.write_bytes(b"tampered")
        # Attempt to generate response should fail at integrity check
        with pytest.raises(Exception) as exc:
            router.generate_response(profile="light", task_type="chat", prompt="hi")
        assert "integrity" in str(exc.value).lower()
    finally:
        monkeypatch.setattr(config_module.settings, "MODEL_PATH", original_model_path)