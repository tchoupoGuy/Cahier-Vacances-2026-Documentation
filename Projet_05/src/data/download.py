"""Téléchargement du jeu de données Kaggle (poissons d'aquarium)."""

from __future__ import annotations

DATASET_SLUG = "mahmoodyousaf/fish-dataset"


def download_dataset(output_dir: str = "data") -> str:
    """Télécharge (une seule fois, mis en cache ensuite) le dataset Kaggle.

    Nécessite un accès réseau et des identifiants Kaggle configurés
    (`kagglehub` gère l'authentification automatiquement).
    """
    import kagglehub

    return kagglehub.dataset_download(DATASET_SLUG, output_dir=output_dir)
