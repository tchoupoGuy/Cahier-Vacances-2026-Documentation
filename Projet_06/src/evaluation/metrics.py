"""Métriques de comparaison des modèles."""

from __future__ import annotations

import numpy as np
import pandas as pd


def mae(y_true, y_pred) -> float:
    """Mean Absolute Error : l'écart moyen, en glaces, entre la réalité et la prévision."""
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def scores_table(scores: dict[str, float]) -> pd.DataFrame:
    """Trie un dict {nom du modèle: MAE} en DataFrame lisible, meilleur modèle en tête."""
    table = pd.DataFrame({"modèle": list(scores), "erreur moyenne (glaces/jour)": list(scores.values())})
    return table.sort_values("erreur moyenne (glaces/jour)").round(2).reset_index(drop=True)
