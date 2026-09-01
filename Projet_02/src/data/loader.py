"""Chargement et filtrage du jeu de données de matchs internationaux."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_URL = "https://github.com/martj42/international_results"

MODERN_ERA_START = "1994-01-01"
MODERN_ERA_END = "2026-06-30"


def load_results(path: str | Path = "data/raw/results.csv") -> pd.DataFrame:
    """Charge le fichier de résultats et ajoute une colonne `year`.

    Renvoie un DataFrame trié par date, index réinitialisé.
    """
    path = Path(path)
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Le fichier '{path}' est introuvable. Télécharge 'results.csv' depuis "
            f"{DATA_URL} et place-le dans 'data/raw/'."
        ) from None

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    return df.sort_values("date").reset_index(drop=True)


def filter_modern_era(
    df: pd.DataFrame, start: str = MODERN_ERA_START, end: str = MODERN_ERA_END
) -> pd.DataFrame:
    """Ne garde que les matchs joués entre `start` et `end` (bornes incluses).

    On se limite à l'ère moderne du football pour que les régularités
    apprises par le modèle restent pertinentes aujourd'hui.
    """
    mask = (df["date"] >= start) & (df["date"] <= end)
    return df[mask].reset_index(drop=True)


def add_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une colonne `outcome` : home_win / draw / away_win."""
    df = df.copy()
    df["outcome"] = "draw"
    df.loc[df["home_score"] > df["away_score"], "outcome"] = "home_win"
    df.loc[df["home_score"] < df["away_score"], "outcome"] = "away_win"
    return df
