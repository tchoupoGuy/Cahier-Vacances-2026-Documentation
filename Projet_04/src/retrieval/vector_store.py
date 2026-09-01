"""Base de données vectorielle minimaliste : un tableau numpy + une recherche par similarité cosinus.

Pour 15 rubriques, un tableau numpy suffit très largement. En production,
sur des milliers/millions de chunks, on remplacerait cette classe par un
vrai index (FAISS, Chroma, Pinecone) sans changer l'interface `search`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class VectorStore:
    def __init__(self, pages: pd.DataFrame, embedder) -> None:
        """
        Arguments
        ---------
        pages -- DataFrame avec une colonne `section` (le texte à indexer)
        embedder -- objet exposant `.encode(list[str], normalize_embeddings=True)`
                    (un SentenceTransformer en production, un objet factice en test)
        """
        self.pages = pages.reset_index(drop=True)
        self.embedder = embedder
        self.chunk_embeddings = embedder.encode(
            self.pages["section"].tolist(), normalize_embeddings=True
        )

    def search(self, question: str, top_k: int = 2) -> pd.DataFrame:
        """Renvoie les `top_k` rubriques les plus proches de la question, avec leur score."""
        question_embedding = self.embedder.encode([question], normalize_embeddings=True)[0]
        similarities = self.chunk_embeddings @ question_embedding
        top_indices = np.argsort(-similarities)[:top_k]

        results = self.pages.iloc[top_indices].copy()
        results["score"] = similarities[top_indices]
        return results
