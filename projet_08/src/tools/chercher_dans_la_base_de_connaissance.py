"""Outil : recherche sémantique dans la base de connaissance (fiches KB)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.embeddings.encoder import encode as default_encode


def chercher_dans_la_base_de_connaissance(
    knowledge_base: pd.DataFrame,
    encoder,
    question: str,
    k: int = 3,
    encode_fn=default_encode,
) -> pd.DataFrame:
    """Trouve les k fiches de la base de connaissance les plus proches d'une question.

    Compare par le SENS (embeddings), pas par mots-clés exacts : "je veux
    supprimer ma commande" doit pouvoir retrouver la fiche "Annuler une
    commande" même sans le mot "annuler".

    Args:
        knowledge_base: le DataFrame INDEXÉ renvoyé par
            `embeddings.encoder.encoder_la_base_de_connaissance` (doit
            contenir une colonne "vecteur" déjà calculée UNE FOIS — voir
            cette fonction pour pourquoi on n'encode plus les 19 fiches à
            chaque question posée).
        encoder: le modèle renvoyé par load_encoder (ou une doublure de test).
        question: la question du client, telle qu'elle est posée.
        k: le nombre de fiches à renvoyer.
        encode_fn: injectable pour les tests (par défaut :
            embeddings.encoder.encode) — permet de tester la mécanique de
            recherche sans télécharger de modèle.

    Returns:
        DataFrame des k meilleures fiches, avec une colonne "score"
        (similarité cosinus, vecteurs normalisés), les meilleures d'abord.
        Le score de la première ligne est ce que la boucle de l'agent devra
        comparer à son seuil de confiance avant de répondre ou d'escalader.
    """
    vecteur_question = encode_fn(encoder, [question])[0]                       # un seul vecteur à chaque appel
    vecteurs_fiches = np.vstack(knowledge_base["vecteur"].to_numpy())           # déjà calculés, jamais recalculés ici

    resultats = knowledge_base.drop(columns="vecteur").copy()
    resultats["score"] = vecteurs_fiches @ vecteur_question                     # vecteurs normalisés = cosinus
    return resultats.sort_values("score", ascending=False).head(k).reset_index(drop=True)
