"""Point d'entrée : entraîne le modèle, l'évalue, puis simule la Coupe du Monde 2030.

Usage :
    python main.py
"""

from __future__ import annotations

from pathlib import Path

from src.pipeline import run_training_pipeline
from src.simulation.tournament import ROUND_OF_32, save_champion_path_chart, simulate_tournament

FIGURES_DIR = Path(__file__).resolve().parent / "reports" / "figures"


def main() -> None:
    result = run_training_pipeline()

    print(f"Baseline (toujours prédire une victoire à domicile) : {result['baseline']:.1%}")
    print(f"Accuracy du modèle : {result['accuracy']:.1%}")

    champion, all_results = simulate_tournament(result["model"], result["scaler"], result["df"], ROUND_OF_32)
    save_champion_path_chart(champion, all_results, FIGURES_DIR)


if __name__ == "__main__":
    main()
