"""Calcul de la forme récente d'une équipe (points, buts marqués/encaissés).

Toute la logique "historique glissant" du projet vit ici, séparée du reste :
c'est un morceau de plomberie réutilisable, indépendant du modèle utilisé
en aval.
"""

from __future__ import annotations

from collections import defaultdict, deque

import pandas as pd


def _points(goals_for: int, goals_against: int) -> int:
    """Nombre de points gagnés pour un match (3 victoire / 1 nul / 0 défaite)."""
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def add_recent_form(df: pd.DataFrame, window: int = 10, min_matches: int = 5) -> pd.DataFrame:
    """Ajoute, pour chaque équipe et chaque match, sa forme AVANT ce match.

    Pour les deux équipes de chaque ligne, calcule la moyenne de points, de
    buts marqués et de buts encaissés sur les `window` derniers matchs
    connus à cette date. En dessous de `min_matches` matchs d'historique,
    la valeur est NaN (pas assez d'informations pour être fiable).

    Returns
    -------
    Une copie de `df` avec 6 nouvelles colonnes :
    home_avg_points, home_avg_goals_scored, home_avg_goals_conceded,
    away_avg_points, away_avg_goals_scored, away_avg_goals_conceded.
    """
    history: dict[str, deque] = defaultdict(lambda: deque(maxlen=window))
    new_columns = []

    for row in df.itertuples():
        features = {}
        for side, team in [("home", row.home_team), ("away", row.away_team)]:
            past = history[team]
            if len(past) >= min_matches:
                features[f"{side}_avg_points"] = sum(m[0] for m in past) / len(past)
                features[f"{side}_avg_goals_scored"] = sum(m[1] for m in past) / len(past)
                features[f"{side}_avg_goals_conceded"] = sum(m[2] for m in past) / len(past)
        new_columns.append(features)

        for team, goals_for, goals_against in [
            (row.home_team, row.home_score, row.away_score),
            (row.away_team, row.away_score, row.home_score),
        ]:
            history[team].append((_points(goals_for, goals_against), goals_for, goals_against))

    form_df = pd.DataFrame(new_columns, index=df.index)
    return pd.concat([df, form_df], axis=1)


def get_current_form(df: pd.DataFrame, team: str, window: int = 10) -> dict:
    """Forme actuelle d'une équipe, calculée sur ses `window` derniers matchs connus.

    Utilisée pour prédire un match futur (pas encore dans l'historique).
    """
    mask = (df["home_team"] == team) | (df["away_team"] == team)
    last_matches = df[mask].tail(window)
    if last_matches.empty:
        raise ValueError(f"Aucun match trouvé pour l'équipe '{team}'. Vérifie l'orthographe (noms en anglais).")

    points, scored, conceded = [], [], []
    for row in last_matches.itertuples():
        if row.home_team == team:
            goals_for, goals_against = row.home_score, row.away_score
        else:
            goals_for, goals_against = row.away_score, row.home_score
        points.append(_points(goals_for, goals_against))
        scored.append(goals_for)
        conceded.append(goals_against)

    n = len(points)
    return {
        "avg_points": sum(points) / n,
        "avg_goals_scored": sum(scored) / n,
        "avg_goals_conceded": sum(conceded) / n,
    }
