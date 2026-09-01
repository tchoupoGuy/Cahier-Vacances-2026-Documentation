"""Pipeline complet : villages bruts -> 21 étapes -> parcours optimisé de chaque étape."""

from __future__ import annotations

from pathlib import Path

from src.clustering.stages import (
    N_STAGES,
    assign_stage_numbers,
    cah_stages,
    compare_clusterings,
    kmeans_stages,
)
from src.data.loader import load_villages, project_to_km
from src.routing.distance import build_distance_matrix
from src.routing.heuristics import best_route

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "villages_2027.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def run_pipeline(villages_path: Path = DATA_PATH) -> dict:
    """Enchaîne les deux missions du Tour 2027 : découper en étapes, puis router chacune.

    Returns un dict avec le DataFrame enrichi, la comparaison des deux
    clusterings, la matrice de distances et le tracé final (chemins + km).
    """
    villages = load_villages(villages_path)
    villages = project_to_km(villages)

    labels_kmeans = kmeans_stages(villages)
    labels_cah = cah_stages(villages)
    comparison = compare_clusterings(villages, labels_kmeans, labels_cah)

    # Mission 1 : on retient le découpage K-Means (voir FEYNMAN.md pour la justification)
    villages = assign_stage_numbers(villages, labels_kmeans)

    distances = build_distance_matrix(villages)

    # Mission 2 : le meilleur parcours (glouton + 2-opt) pour chaque étape
    stage_paths: dict[int, list[int]] = {}
    stage_distances: dict[int, float] = {}
    for stage in range(1, N_STAGES + 1):
        stage_indices = list(villages.index[villages["stage"] == stage])
        path, distance = best_route(stage_indices, distances)
        stage_paths[stage] = path
        stage_distances[stage] = distance

    return {
        "villages": villages,
        "labels_kmeans": labels_kmeans,
        "labels_cah": labels_cah,
        "comparison": comparison,
        "distances": distances,
        "stage_paths": stage_paths,
        "stage_distances": stage_distances,
        "total_distance": sum(stage_distances.values()),
    }
