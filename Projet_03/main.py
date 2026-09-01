"""Point d'entrée : construit le Tour de France 2027 complet.

Usage :
    python main.py
"""

from __future__ import annotations

from pathlib import Path

from src.pipeline import FIGURES_DIR, run_pipeline
from src.roadbook import print_roadbook
from src.visualization.maps import plot_final_tour, plot_stage_sizes, plot_stages, plot_villages


def main() -> None:
    result = run_pipeline()
    villages = result["villages"]
    comparison = result["comparison"]

    print(
        f"Silhouette K-Means : {comparison['silhouette_kmeans']:.3f} | "
        f"étapes de {comparison['sizes_kmeans'].min()} à {comparison['sizes_kmeans'].max()} villages"
    )
    print(
        f"Silhouette CAH     : {comparison['silhouette_cah']:.3f} | "
        f"étapes de {comparison['sizes_cah'].min()} à {comparison['sizes_cah'].max()} villages"
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_villages(villages, "Les 120 villages-étapes du Tour 2027", FIGURES_DIR / "villages.png")
    plot_stages(
        villages, villages["stage"], "Les 21 étapes officielles du Tour 2027",
        FIGURES_DIR / "stages.png", numbered=True,
    )
    plot_stage_sizes(comparison["sizes_kmeans"], comparison["sizes_cah"], FIGURES_DIR / "stage_sizes.png")
    plot_final_tour(villages, result["stage_paths"], result["stage_distances"], FIGURES_DIR / "final_tour.png")

    print_roadbook(villages, result["stage_paths"], result["stage_distances"])
    print(f"\nDistance totale du Tour 2027 : {result['total_distance']:.0f} km")


if __name__ == "__main__":
    main()
