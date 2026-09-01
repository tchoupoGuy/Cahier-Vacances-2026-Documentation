"""Distances géographiques : formule de haversine et matrice de distances."""

from __future__ import annotations

import math

import pandas as pd

EARTH_RADIUS_KM = 6371


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance à vol d'oiseau entre deux points GPS, en kilomètres."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def build_distance_matrix(villages: pd.DataFrame) -> list[list[float]]:
    """Matrice n x n des distances haversine entre chaque paire de villages."""
    coords = list(zip(villages["latitude"], villages["longitude"]))
    n = len(coords)
    return [
        [haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1]) for j in range(n)]
        for i in range(n)
    ]


def path_distance(path: list[int], distances: list[list[float]]) -> float:
    """Longueur totale d'un parcours ouvert (pas de retour au point de départ)."""
    return sum(distances[path[i]][path[i + 1]] for i in range(len(path) - 1))
