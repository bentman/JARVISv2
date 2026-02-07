from __future__ import annotations
import numpy as np
import hashlib
from typing import List
from app.core.config import settings


class EmbeddingService:
    """
    Lightweight, local-first embedding service using feature hashing.
    - No external model downloads required.
    - Produces deterministic fixed-size embeddings suitable for approximate semantic search.
    """

    def __init__(self, dim: int | None = None):
        self.dim: int = dim or settings.EMBEDDING_DIM

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace + punctuation split; lowercase for normalization
        import re
        return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]

    def _hash_token(self, token: str) -> int:
        # Use sha1 for stable hashing across runs/platforms
        h = hashlib.sha1(token.encode("utf-8")).hexdigest()
        # Map to integer and then to vector dimension range
        return int(h, 16) % self.dim

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Returns a numpy array of shape (len(texts), dim) with L2-normalized embeddings
        """
        mat = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            for tok in tokens:
                idx = self._hash_token(tok)
                mat[i, idx] += 1.0
        # L2 normalize
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        mat = mat / norms
        return mat


# Global instance
embedding_service = EmbeddingService()