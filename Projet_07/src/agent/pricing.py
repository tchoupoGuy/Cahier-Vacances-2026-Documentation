"""Chiffrage d'un voyage et exploration des dates voisines."""

from __future__ import annotations

from datetime import datetime, timedelta


def price_trip(vol, hotel, activites: list[dict], nuits: int) -> float:
    """Calcule le prix total d'un voyage, PAR PERSONNE (l'hôtel aussi).

    Arguments
    ---------
    vol -- une ligne du DataFrame des vols
    hotel -- une ligne du DataFrame des hôtels
    activites -- une liste de dicts, chacun avec une clé "prix_eur"
    nuits -- le nombre de nuits
    """
    prix_vol = vol["prix_eur"]
    prix_hotel = hotel["prix_nuit"] * nuits
    prix_activites = sum(a["prix_eur"] for a in activites)
    return float(prix_vol + prix_hotel + prix_activites)


def neighbouring_dates(date_depart: str, ecart: int = 2) -> list[str]:
    """Les jours à explorer autour de la date demandée, du plus proche au plus lointain.

    Arguments
    ---------
    date_depart -- le jour souhaité, au format "2026-08-12"
    ecart -- de combien de jours on accepte de s'éloigner
    """
    jour = datetime.strptime(date_depart, "%Y-%m-%d")
    voisines = []
    for decalage in range(1, ecart + 1):
        for signe in (-1, 1):
            voisines.append((jour + timedelta(days=signe * decalage)).strftime("%Y-%m-%d"))
    return voisines
