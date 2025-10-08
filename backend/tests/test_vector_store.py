import os
import tempfile
from app.services.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService


def test_vector_store_add_and_search():
    # Use temp directory for index/meta
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "test.index")
        meta_path = os.path.join(tmpdir, "test_meta.json")
        vs = VectorStore(dim=64, index_path=index_path, meta_path=meta_path)

        texts = [
            "The quick brown fox jumps over the lazy dog",
            "A fast auburn fox leaps above a sleepy canine",
            "Quantum mechanics deals with the behavior of particles",
        ]
        metas = [
            {"id": "t1"},
            {"id": "t2"},
            {"id": "t3"},
        ]
        ids = vs.add_texts(texts, metas)
        assert len(ids) == 3

        # Query semantically similar to the first two
        results = vs.search("quick fox over dog", k=2)
        assert len(results) >= 1
        # Ensure metadata present
        score, meta = results[0]
        assert isinstance(score, float)
        assert "id" in meta
