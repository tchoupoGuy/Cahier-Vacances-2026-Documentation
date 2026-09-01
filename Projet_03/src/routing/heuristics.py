"""Heuristiques de résolution du problème du voyageur de commerce (TSP).

Deux briques indépendantes, combinables : une construction gloutonne
(rapide, approximative) suivie d'une amélioration locale (2-opt).
"""

from __future__ import annotations

from src.routing.distance import path_distance


def greedy_path(indices: list[int], start: int, distances: list[list[float]]) -> list[int]:
    """Construit un parcours par plus-proche-voisin : à chaque pas, va au village
    non visité le plus proche du village courant.

    Rapide, jamais garanti optimal (algorithme glouton).
    """
    unvisited = set(indices)
    path = [start]
    unvisited.remove(start)
    while unvisited:
        path.append(min(unvisited, key=lambda j: distances[path[-1]][j]))
        unvisited.remove(path[-1])
    return path


def two_opt(path: list[int], distances: list[list[float]]) -> list[int]:
    """Améliore un parcours en "décroisant" des segments tant que ça raccourcit le trajet.

    Le glouton peut laisser des croisements dans le tracé ; 2-opt les corrige
    par recherche locale, sans jamais dégrader la distance totale.
    """
    path = path.copy()

    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                a, b, c, d = path[i - 1], path[i], path[j], path[j + 1]
                if distances[a][c] + distances[b][d] < distances[a][b] + distances[c][d] - 1e-10:
                    path[i:j + 1] = reversed(path[i:j + 1])
                    improved = True
    return path


def best_route(indices: list[int], distances: list[list[float]]) -> tuple[list[int], float]:
    """Essaie chaque village comme point de départ (glouton + 2-opt) et garde le meilleur.

    Returns (meilleur_parcours, distance_totale).
    """
    best_distance = float("inf")
    best_path: list[int] | None = None

    for start in indices:
        path = greedy_path(indices, start, distances)
        improved_path = two_opt(path, distances)
        distance = path_distance(improved_path, distances)
        if distance < best_distance:
            best_distance = distance
            best_path = improved_path

    return best_path, best_distance
