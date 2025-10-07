from __future__ import annotations
import json
import os
from typing import List, Dict, Any, Optional, Tuple
import faiss
import numpy as np
from app.core.config import settings
from app.services.embedding_service import embedding_service


class VectorStore:
    """
    FAISS-based vector store for semantic search over messages.
    - Persists index to disk (settings.VECTOR_INDEX_PATH)
    - Persists metadata mapping (vector_id -> dict) to disk (settings.VECTOR_META_PATH)
    """
    def __init__(self, dim: Optional[int] = None, index_path: Optional[str] = None, meta_path: Optional[str] = None):
        self.dim = dim or settings.EMBEDDING_DIM
        self.index_path = index_path or settings.VECTOR_INDEX_PATH
        self.meta_path = meta_path or settings.VECTOR_META_PATH
        self._index = None  # type: Optional[faiss.IndexFlatIP]
        self._meta: Dict[int, Dict[str, Any]] = {}
        self._load()

    @property
    def available(self) -> bool:
        return self._index is not None

    def _create_index(self) -> faiss.IndexFlatIP:
        index = faiss.IndexFlatIP(self.dim)
        return index

    def _load(self) -> None:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(self.meta_path) or ".", exist_ok=True)
        # Load index if exists
        if os.path.exists(self.index_path):
            self._index = faiss.read_index(self.index_path)
        else:
            self._index = self._create_index()
        # Load meta if exists
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta_loaded = json.load(f)
                    # keys are stored as strings in JSON
                    self._meta = {int(k): v for k, v in meta_loaded.items()}
            except Exception:
                self._meta = {}

    def _persist(self) -> None:
        if self._index is not None:
            faiss.write_index(self._index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in self._meta.items()}, f)

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[int]:
        assert len(texts) == len(metadatas)
        if not texts:
            return []
        vecs = embedding_service.embed_texts(texts)  # shape (n, dim)
        # FAISS IndexFlatIP expects float32 and works best with normalized vectors
        ids_start = self._index.ntotal if self._index is not None else 0
        self._index.add(vecs)
        assigned_ids = list(range(ids_start, ids_start + len(texts)))
        for idx, meta in zip(assigned_ids, metadatas):
            self._meta[idx] = meta
        self._persist()
        return assigned_ids

    def search(self, query: str, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        if not query or self._index is None or self._index.ntotal == 0:
            return []
        qvec = embedding_service.embed_texts([query])  # (1, dim)
        scores, indices = self._index.search(qvec, min(k, self._index.ntotal))  # scores inner product
        result: List[Tuple[float, Dict[str, Any]]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self._meta.get(int(idx))
            if meta is not None:
                result.append((float(score), meta))
        return result


# Global instance
vector_store = VectorStore()