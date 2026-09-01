"""Encodeur de phrases : transforme un texte en vecteur, pour comparer par le sens."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_encoder(model_name: str = DEFAULT_MODEL):
    """Charge le modèle d'embeddings qui rapprochera une question client des fiches KB.

    Import local : le reste du package n'a pas besoin de
    `sentence-transformers` pour être testé (une doublure suffit, même
    principe qu'au Projet 04/07).

    Ne capture pas l'échec de téléchargement : le journalise (la cause la
    plus fréquente — pas de réseau — n'est pas toujours évidente depuis la
    trace Hugging Face brute) puis relance, pour que l'appelant décide quoi
    faire (main.py, par exemple, s'arrête proprement plutôt que de crasher
    au milieu d'une démo).
    """
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name)
    except Exception:
        logger.exception(
            "échec du chargement du modèle d'embeddings '%s' — la cause la plus "
            "fréquente est l'absence d'accès réseau (le modèle doit être "
            "téléchargé depuis Hugging Face au premier appel)",
            model_name,
        )
        raise


def encode(encoder, texts) -> "np.ndarray":
    """Transforme une liste de textes en vecteurs normalisés (longueur 1).

    Normalisés : la similarité cosinus entre deux vecteurs se réduit à leur
    simple produit scalaire.
    """
    return encoder.encode(list(texts), normalize_embeddings=True)


def encoder_la_base_de_connaissance(knowledge_base: pd.DataFrame, encoder, encode_fn=encode) -> pd.DataFrame:
    """Calcule UNE FOIS le vecteur de chaque fiche — à appeler après `load_knowledge_base()`,
    jamais à l'intérieur de la boucle qui traite les questions.

    Sans cette étape séparée, `chercher_dans_la_base_de_connaissance` devrait
    ré-encoder les mêmes 19 fiches à CHAQUE question posée par CHAQUE client
    — un recalcul entièrement inutile, puisque le contenu des fiches ne
    change jamais entre deux questions. Cette fonction sépare explicitement
    l'INDEXATION (une fois, coûteuse : toute la base) de la RECHERCHE (à
    chaque question, bon marché : une seule phrase à encoder).

    Args:
        knowledge_base: le DataFrame renvoyé par `load_knowledge_base`.
        encoder: le modèle renvoyé par `load_encoder` (ou une doublure de test).
        encode_fn: injectable pour les tests (par défaut : `encode`).

    Returns:
        Une COPIE de `knowledge_base`, avec une colonne "vecteur" en plus —
        c'est cette version indexée qu'il faut passer à
        `chercher_dans_la_base_de_connaissance`, pas le DataFrame brut.
    """
    resultat = knowledge_base.copy()
    resultat["vecteur"] = list(encode_fn(encoder, knowledge_base["a_encoder"]))
    return resultat
