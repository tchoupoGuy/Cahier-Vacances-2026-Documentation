"""Découpage des villages en 21 étapes : deux algorithmes comparés."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score

N_STAGES = 21


def kmeans_stages(villages: pd.DataFrame, n_stages: int = N_STAGES, random_state: int = 42):
    """Découpe en n_stages groupes avec K-Means (centres mobiles)."""
    kmeans = KMeans(n_clusters=n_stages, random_state=random_state, n_init=10)
    return kmeans.fit_predict(villages[["x_km", "y_km"]])


def cah_stages(villages: pd.DataFrame, n_stages: int = N_STAGES):
    """Découpe en n_stages groupes avec la Classification Ascendante Hiérarchique.

    Contrairement à K-Means, aucun tirage aléatoire : le résultat est
    toujours identique d'une exécution à l'autre.
    """
    return AgglomerativeClustering(n_clusters=n_stages, linkage="ward").fit_predict(
        villages[["x_km", "y_km"]]
    )


def compare_clusterings(villages: pd.DataFrame, labels_kmeans, labels_cah) -> dict:
    """Compare les deux découpages avec le score de silhouette et la taille des groupes."""
    features = villages[["x_km", "y_km"]]
    sizes_kmeans = pd.Series(labels_kmeans).value_counts()
    sizes_cah = pd.Series(labels_cah).value_counts()

    return {
        "silhouette_kmeans": silhouette_score(features, labels_kmeans),
        "silhouette_cah": silhouette_score(features, labels_cah),
        "sizes_kmeans": sizes_kmeans,
        "sizes_cah": sizes_cah,
    }


def assign_stage_numbers(villages: pd.DataFrame, labels) -> pd.DataFrame:
    """Numérote les étapes de 1 à N, du nord vers le sud (plus lisible qu'un numéro arbitraire)."""
    villages = villages.copy()
    villages["stage"] = labels

    stage_order = villages.groupby("stage")["latitude"].mean().sort_values(ascending=False).index
    villages["stage"] = villages["stage"].map({old: new + 1 for new, old in enumerate(stage_order)})
    return villages
