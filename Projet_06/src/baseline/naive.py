"""Réflexes naïfs de Bruno, servant de point de comparaison honnête aux modèles."""

from __future__ import annotations

import numpy as np


def baseline_mean(train: np.ndarray, n_test: int) -> np.ndarray:
    """"Toujours prédire la moyenne historique"."""
    return np.full(n_test, train.mean())


def baseline_yesterday(full_series: np.ndarray, n_test: int) -> np.ndarray:
    """"Comme hier" : prédit la valeur du jour précédent pour chaque jour de test."""
    start = len(full_series) - n_test
    return full_series[start - 1: start - 1 + n_test]
