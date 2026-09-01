"""Chargement des villages et projection des coordonnées GPS en kilomètres."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


def load_villages(path: str | Path) -> pd.DataFrame:
    """Charge les 120 villages-étapes du Tour 2027.

    Returns un DataFrame avec les colonnes village, departement, latitude, longitude.
    """
    path = Path(path)
    try:
        villages = pd.read_csv(path, dtype={"departement": str})
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Le fichier '{path}' est introuvable. Il doit se trouver dans data/."
        ) from None
    return villages


def project_to_km(villages: pd.DataFrame) -> pd.DataFrame:
    """Ajoute des colonnes x_km / y_km : les coordonnées GPS projetées en kilomètres.

    Un degré de longitude ne vaut pas la même distance qu'un degré de latitude
    (les méridiens se resserrent en s'éloignant de l'équateur) : on corrige
    avec cos(latitude moyenne) pour que les distances calculées ensuite sur
    (x_km, y_km) soient géométriquement correctes.
    """
    villages = villages.copy()
    lat_mean = villages["latitude"].mean()

    villages["y_km"] = villages["latitude"] * 111
    villages["x_km"] = villages["longitude"] * 111 * math.cos(math.radians(lat_mean))

    return villages
