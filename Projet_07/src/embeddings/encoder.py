"""Encodeur de phrases : le même modèle d'embeddings que le Projet 04."""

from __future__ import annotations

DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_encoder(model_name: str = DEFAULT_MODEL):
    """Charge le modèle d'embeddings qui rapprochera une envie des brochures.

    Import local : le reste du package n'a pas besoin de
    `sentence-transformers` pour être testé (voir tests/fakes.py).
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def encode(encoder, texts) -> "np.ndarray":
    """Transforme une liste de textes en vecteurs normalisés (longueur 1).

    Normalisés : la similarité cosinus entre deux vecteurs se réduit à leur
    simple produit scalaire.
    """
    return encoder.encode(list(texts), normalize_embeddings=True)
