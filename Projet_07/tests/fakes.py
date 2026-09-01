"""Doublure d'encodeur pour tester la recherche sémantique sans télécharger de modèle.

Même principe qu'au Projet 04 : un encodeur factice qui compte la présence
de quelques mots-clés. Ce n'est pas un vrai embedding sémantique, mais ça
suffit à vérifier que la mécanique (encoder, comparer, trier) fonctionne.
"""

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
    """Signature compatible avec `encode_fn` de `find_hotels` / `embeddings.encoder.encode`."""
    return encoder.encode(list(texts), normalize_embeddings=True)
