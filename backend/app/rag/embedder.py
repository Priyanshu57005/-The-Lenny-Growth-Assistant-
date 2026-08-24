import logging
from typing import List
import numpy as np

logger = logging.getLogger("lenny_growth.rag.embedder")

class VectorEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to simple TF-IDF embedding.")
                self._model = "fallback"

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        if self._model != "fallback":
            vec = self._model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        else:
            # Fallback deterministic pseudo-embedding vector of size 384
            words = text.lower().split()
            vec = np.zeros(384, dtype=np.float32)
            for i, word in enumerate(words):
                idx = abs(hash(word)) % 384
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

embedder = VectorEmbedder()
