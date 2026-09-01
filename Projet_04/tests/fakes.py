"""Doublures de test pour l'embedder et le générateur.

Les vrais modèles (SentenceTransformer, Qwen) nécessitent un accès réseau
pour être téléchargés depuis Hugging Face. Ces classes factices permettent
de tester toute la logique du RAG (recherche, prompt, orchestration) sans
dépendre du réseau ni d'un GPU.
"""

from __future__ import annotations

import re

import numpy as np


class FakeEmbedder:
    """Encode un texte en comptant l'occurrence de mots d'un vocabulaire fixe.

    Ce n'est pas un vrai embedding sémantique, mais ça se comporte pareil
    pour ce qu'on veut tester : deux textes qui partagent des mots-clés se
    retrouvent proches au sens du produit scalaire.
    """

    def __init__(self, vocabulary: list[str]):
        self.vocabulary = [w.lower() for w in vocabulary]

    def encode(self, texts: list[str], normalize_embeddings: bool = False) -> np.ndarray:
        vectors = []
        for text in texts:
            words = set(re.findall(r"[a-zàâäéèêëïîôöùûüç\-]+", text.lower()))
            vector = np.array([1.0 if w in words else 0.0 for w in self.vocabulary])
            if normalize_embeddings and np.linalg.norm(vector) > 0:
                vector = vector / np.linalg.norm(vector)
            vectors.append(vector)
        return np.array(vectors)


class FakeGenerator:
    """Simule le pipeline `text-generation` de transformers, sans télécharger de modèle."""

    def __call__(self, prompt, max_length=None, max_new_tokens=None, do_sample=None):
        if isinstance(prompt, list):  # mode "conversation" (ask_llm)
            return [{"generated_text": [*prompt, {"role": "assistant", "content": "réponse factice"}]}]
        return [{"generated_text": f"{prompt}\nréponse factice"}]
