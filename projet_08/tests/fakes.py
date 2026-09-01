"""Doublure d'encodeur pour tester la recherche sémantique et la boucle sans télécharger de modèle."""

from __future__ import annotations

import re

import numpy as np


class FakeEncoder:
    def __init__(self, vocabulary: list[str]):
        self.vocabulary = [w.lower() for w in vocabulary]

    def encode(self, texts, normalize_embeddings: bool = False) -> np.ndarray:
        vectors = []
        for text in texts:
            words = set(re.findall(r"[a-zàâäéèêëïîôöùûüç\-]+", text.lower()))
            vector = np.array([1.0 if w in words else 0.0 for w in self.vocabulary])
            if normalize_embeddings and np.linalg.norm(vector) > 0:
                vector = vector / np.linalg.norm(vector)
            vectors.append(vector)
        return np.array(vectors)


def fake_encode(encoder, texts):
    """Signature compatible avec `encode_fn` de `chercher_dans_la_base_de_connaissance`."""
    return encoder.encode(list(texts), normalize_embeddings=True)
