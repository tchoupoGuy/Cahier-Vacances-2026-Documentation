"""Prédiction d'un match unique à partir du modèle entraîné."""

from __future__ import annotations

import pandas as pd

from src.features.engineering import FEATURES
from src.features.form import get_current_form


def _match_features(df: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    """Construit la ligne de features pour un match A vs B sur terrain neutre."""
    form_a = get_current_form(df, team_a)
    form_b = get_current_form(df, team_b)

    row = {
        "diff_avg_points": form_a["avg_points"] - form_b["avg_points"],
        "diff_avg_goals_scored": form_a["avg_goals_scored"] - form_b["avg_goals_scored"],
        "diff_avg_goals_conceded": form_a["avg_goals_conceded"] - form_b["avg_goals_conceded"],
        "is_neutral": 1,
        "is_friendly": 0,
    }
    return pd.DataFrame([row], columns=FEATURES)


def predict_match(model, scaler, df: pd.DataFrame, team_a: str, team_b: str) -> tuple[str, float]:
    """Prédit le vainqueur d'un match A vs B sur terrain neutre.

    Returns
    -------
    (vainqueur, probabilité associée) — la probabilité est toujours >= 0.5,
    c'est celle du vainqueur prédit, pas celle de `team_a` en particulier.
    """
    features = _match_features(df, team_a, team_b)
    features_scaled = scaler.transform(features)
    proba_a_wins = model.predict_proba(features_scaled)[0, 1]

    if proba_a_wins >= 0.5:
        return team_a, proba_a_wins
    return team_b, 1 - proba_a_wins
