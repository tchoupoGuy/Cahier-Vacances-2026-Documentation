"""Outil n°1 de l'agent : trouver des vols (SQL paramétré sur la base voyages.db)."""

from __future__ import annotations

import sqlite3

import pandas as pd

from src.data.database import query

SQL_VOLS = """
    SELECT numero, origine, heure_depart, duree_h, prix_eur, places_restantes
    FROM vols
    WHERE destination = ? AND date_depart = ? AND places_restantes >= ?
    ORDER BY prix_eur
"""


def find_flights(conn: sqlite3.Connection, destination: str, date_depart: str, voyageurs: int = 1) -> pd.DataFrame:
    """Trouve les vols disponibles vers une destination, un jour donné.

    Arguments
    ---------
    destination -- le nom de la ville, tel qu'écrit dans la table
    date_depart -- le jour du départ, au format "2026-08-12"
    voyageurs -- le nombre de places nécessaires

    Returns
    -------
    DataFrame des vols trouvés, du moins cher au plus cher.
    """
    return query(conn, SQL_VOLS, (destination, date_depart, voyageurs))
