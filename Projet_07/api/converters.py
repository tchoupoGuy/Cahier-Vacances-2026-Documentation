"""Convertit entre les objets internes de `src/` (DataFrame, pandas.Series, dict)
et les schémas Pydantic de l'API (JSON-safe).

C'est la seule couche qui connaît les deux mondes à la fois : `src/` ne sait
pas que l'API existe, et l'API ne fait jamais de calcul métier elle-même —
elle appelle `src/` puis reformate. Si demain l'agent change de forme
interne, seul ce fichier bouge.
"""

from __future__ import annotations


def flight_to_dict(vol) -> dict:
    """pandas.Series (une ligne de `find_flights`) -> dict JSON-safe."""
    return {
        "numero": str(vol["numero"]),
        "origine": str(vol["origine"]),
        "heure_depart": str(vol["heure_depart"]),
        "duree_h": float(vol["duree_h"]),
        "prix_eur": float(vol["prix_eur"]),
        "places_restantes": int(vol["places_restantes"]),
    }


def hotel_to_dict(hotel) -> dict:
    """pandas.Series (une ligne de `find_hotels`) -> dict JSON-safe."""
    return {
        "hotel": str(hotel["hotel"]),
        "ville": str(hotel["ville"]),
        "etoiles": int(hotel["etoiles"]),
        "prix_nuit": float(hotel["prix_nuit"]),
        "note": float(hotel["note"]),
        "avis": int(hotel["avis"]),
        "resume": str(hotel["resume"]),
        "score": float(hotel["score"]),
    }


def activity_to_dict(activite: dict) -> dict:
    """Une entrée de `voyage["activites"]` -> dict JSON-safe (déjà presque un dict)."""
    return {
        "nom": str(activite["nom"]),
        "categorie": str(activite["categorie"]),
        "duree_h": float(activite["duree_h"]),
        "prix_eur": float(activite["prix_eur"]),
    }


def trip_to_dict(voyage: dict) -> dict:
    """Le `voyage` renvoyé par `plan_trip`/`try_one_date` -> dict JSON-safe (forme de TripOut)."""
    return {
        "destination": voyage["destination"],
        "date_depart": voyage["date_depart"],
        "nuits": voyage["nuits"],
        "voyageurs": voyage["voyageurs"],
        "vol": flight_to_dict(voyage["vol"]),
        "hotel": hotel_to_dict(voyage["hotel"]),
        "activites": [activity_to_dict(a) for a in voyage["activites"]],
        "prix_total": float(voyage["prix_total"]),
        "budget_max": float(voyage["budget_max"]),
    }
