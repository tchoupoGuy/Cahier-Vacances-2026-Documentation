"""Outil n°3 de l'agent : trouver des hôtels par recherche sémantique dans les brochures.

Contrairement aux deux outils SQL, les hôtels sont décrits en texte libre :
aucune colonne ne dit "calme" ou "en famille". On compare donc par le SENS,
avec les embeddings du Projet 04, pas par mots-clés.
"""

from __future__ import annotations

import pandas as pd

from src.embeddings.encoder import encode as default_encode


def find_hotels(brochures: pd.DataFrame, encoder, ville: str, envie: str, k: int = 3,
                 encode_fn=default_encode) -> pd.DataFrame:
    """Trouve les k hôtels d'une ville qui correspondent le mieux à une envie écrite librement.

    Arguments
    ---------
    brochures -- le DataFrame renvoyé par load_brochures
    encoder -- le modèle renvoyé par load_encoder (ou une doublure de test)
    ville -- le nom de la ville
    envie -- ce que cherche le voyageur, avec ses mots à lui
    k -- le nombre d'hôtels à retourner
    encode_fn -- injectable pour les tests (par défaut : embeddings.encoder.encode)

    Returns
    -------
    DataFrame des k meilleures brochures, avec une colonne "score", les
    meilleures d'abord.
    """
    hotels_ville = brochures[brochures["ville"] == ville].reset_index(drop=True)

    vecteurs = encode_fn(encoder, hotels_ville["resume"])          # une ligne par hôtel
    vecteur_envie = encode_fn(encoder, [envie])[0]                  # un seul vecteur

    hotels_ville["score"] = vecteurs @ vecteur_envie                # vecteurs normalisés = cosinus
    return hotels_ville.sort_values("score", ascending=False).head(k).reset_index(drop=True)
