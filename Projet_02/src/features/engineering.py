"""Construction des features et de la cible pour l'entraînement du modèle."""

from __future__ import annotations

import pandas as pd

FEATURES = [
    "diff_avg_points",
    "diff_avg_goals_scored",
    "diff_avg_goals_conceded",
    "is_neutral",
    "is_friendly",
]


def build_training_table(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme le DataFrame de matchs (avec forme récente) en table d'entraînement.

    Étapes :
    1. écarte les matchs nuls (on prédit une victoire à domicile ou non)
    2. encode la cible `home_win` (1 si l'équipe à domicile gagne, 0 sinon)
    3. encode les catégories en 0/1 (`is_neutral`, `is_friendly`)
    4. calcule les features différentielles (domicile moins extérieur)
    """
    data = df[df["home_score"] != df["away_score"]].copy()
    data["home_win"] = (data["home_score"] > data["away_score"]).astype(int)

    data["is_neutral"] = data["neutral"].astype(int)
    data["is_friendly"] = (data["tournament"] == "Friendly").astype(int)

    data["diff_avg_points"] = data["home_avg_points"] - data["away_avg_points"]
    data["diff_avg_goals_scored"] = data["home_avg_goals_scored"] - data["away_avg_goals_scored"]
    data["diff_avg_goals_conceded"] = data["home_avg_goals_conceded"] - data["away_avg_goals_conceded"]

    return data


def split_features_target(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = data[FEATURES]
    y = data["home_win"]
    return X, y
