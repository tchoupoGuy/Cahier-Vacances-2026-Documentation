"""Simulation d'un tournoi à élimination directe, match après match.

Contient aussi le petit "affichage" (drapeaux, mise en forme des tours) :
c'est de la plomberie, séparée du raisonnement de simulation lui-même.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.models.predict import predict_match

FLAGS = {
    "Spain": "🇪🇸", "Portugal": "🇵🇹", "Morocco": "🇲🇦", "France": "🇫🇷",
    "Brazil": "🇧🇷", "Argentina": "🇦🇷", "England": "🏴", "Germany": "🇩🇪",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Croatia": "🇭🇷", "Italy": "🇮🇹",
    "Uruguay": "🇺🇾", "Colombia": "🇨🇴", "Japan": "🇯🇵", "United States": "🇺🇸",
    "Mexico": "🇲🇽", "Senegal": "🇸🇳", "Switzerland": "🇨🇭", "Denmark": "🇩🇰",
    "South Korea": "🇰🇷", "Australia": "🇦🇺", "Canada": "🇨🇦", "Ghana": "🇬🇭",
    "Poland": "🇵🇱", "Austria": "🇦🇹", "Turkey": "🇹🇷", "Ecuador": "🇪🇨",
    "Nigeria": "🇳🇬", "Serbia": "🇷🇸", "Greece": "🇬🇷", "Egypt": "🇪🇬",
}

ROUND_NAMES = [
    "Seizièmes de finale",
    "Huitièmes de finale",
    "Quarts de finale",
    "Demi-finales",
    "Finale",
]

ROUND_OF_32 = [
    ("Spain", "Greece"), ("Denmark", "Ecuador"),
    ("Argentina", "Egypt"), ("Netherlands", "Poland"),
    ("France", "Nigeria"), ("Croatia", "South Korea"),
    ("England", "Canada"), ("Italy", "Senegal"),
    ("Portugal", "Australia"), ("Belgium", "Turkey"),
    ("Brazil", "Ghana"), ("Uruguay", "Switzerland"),
    ("Morocco", "Serbia"), ("Mexico", "Austria"),
    ("Germany", "Colombia"), ("Japan", "United States"),
]


def team_label(team: str) -> str:
    return f"{FLAGS.get(team, '🏳️')} {team}"


def simulate_tournament(model, scaler, df: pd.DataFrame, round_of_32: list[tuple[str, str]] = ROUND_OF_32):
    """Simule le tournoi entier, tour après tour, jusqu'au champion.

    Returns
    -------
    (champion, all_results) où `all_results` est la liste de tous les
    matchs simulés sous la forme (team_a, team_b, winner, probability).
    """
    current_round = round_of_32
    all_results = []
    winners: list[str] = []

    for round_name in ROUND_NAMES:
        results = []
        winners = []
        for team_a, team_b in current_round:
            winner, probability = predict_match(model, scaler, df, team_a, team_b)
            results.append((team_a, team_b, winner, probability))
            winners.append(winner)

        _print_round(round_name, results)
        all_results.extend(results)
        current_round = list(zip(winners[::2], winners[1::2]))

    champion = winners[0]
    _print_champion(champion)
    return champion, all_results


def _print_round(round_name: str, match_results) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {round_name.upper()}")
    print("=" * 60)
    for team_a, team_b, winner, probability in match_results:
        line = f"{team_label(team_a):<22} vs {team_label(team_b):<22}"
        print(f"{line} -> {team_label(winner)} ({probability:.0%})")


def _print_champion(team: str) -> None:
    print(f"\n{'*' * 60}")
    print(f"   🏆 CHAMPION DU MONDE 2030 : {team_label(team).upper()} 🏆")
    print("*" * 60)


def save_champion_path_chart(champion: str, all_results, figures_dir) -> None:
    """Trace la probabilité de victoire du champion à chaque tour."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    champion_matches = [match for match in all_results if match[2] == champion]
    opponents = [
        f"{name}\nvs {team_a if team_b == champion else team_b}"
        for name, (team_a, team_b, _, _) in zip(ROUND_NAMES, champion_matches)
    ]
    probabilities = [match[3] for match in champion_matches]

    bars = plt.bar(opponents, probabilities, color="goldenrod")
    plt.axhline(0.5, color="gray", linestyle="--", alpha=0.7, label="Pile ou face (50%)")
    plt.ylim(0, 1)
    plt.ylabel("Probabilité de victoire prédite")
    plt.title(f"Le parcours de {champion} vers le titre 2030")
    plt.legend()
    for bar, prob in zip(bars, probabilities):
        plt.text(bar.get_x() + bar.get_width() / 2, prob + 0.02, f"{prob:.0%}", ha="center")
    plt.tight_layout()
    plt.savefig(figures_dir / "champion_path.png", dpi=150)
    plt.close()
