"""Semantic similarity eval using sentence-transformers."""
from __future__ import annotations
from functools import lru_cache
from app.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def _model():
    from sentence_transformers import SentenceTransformer
    logger.info("Loading sentence-transformer model")
    return SentenceTransformer("all-MiniLM-L6-v2")


def similarity(text_a: str, text_b: str) -> float:
    """Returns cosine similarity [0, 1] between two texts."""
    import numpy as np

    model = _model()
    embs = model.encode([text_a, text_b], normalize_embeddings=True)
    score = float(np.dot(embs[0], embs[1]))
    score = max(0.0, min(1.0, score))
    logger.debug("Semantic similarity computed", extra={"score": round(score, 3)})
    return score
