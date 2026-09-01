"""Chargement du modèle d'embedding (transforme du texte en vecteurs de sens)."""

from __future__ import annotations

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384


def load_embedder(model_name: str = EMBEDDING_MODEL):
    """Charge le modèle d'embedding multilingue.

    Importé ici (pas en haut du module) pour que le reste du package reste
    utilisable sans avoir `sentence-transformers` installé (ex. tests qui
    injectent un embedder factice).
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)
