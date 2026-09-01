"""Chargement du carnet de ventes et découpage chronologique train/test."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_sales(path: str | Path) -> pd.DataFrame:
    """Charge le carnet de ventes de glaces (date, saison, ventes)."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def train_test_split_series(ventes: np.ndarray, dates: pd.Series, n_test: int):
    """Découpe la série dans l'ORDRE CHRONOLOGIQUE : le test, c'est toujours la fin.

    Contrairement à un découpage aléatoire, mélanger les dates n'aurait
    aucun sens ici : on doit prédire le futur à partir du passé.
    """
    train, test = ventes[:-n_test], ventes[-n_test:]
    dates_test = dates.iloc[-n_test:]
    return train, test, dates_test
