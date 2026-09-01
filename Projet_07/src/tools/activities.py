"""Outil n°2 de l'agent : lister les activités d'une ville (SQL paramétré)."""

from __future__ import annotations

import sqlite3

import pandas as pd

from src.data.database import query

SQL_ACTIVITES = """
    SELECT nom, categorie, duree_h, prix_eur
    FROM activites
    WHERE ville = ?
    ORDER BY prix_eur
"""


def find_activities(conn: sqlite3.Connection, ville: str) -> pd.DataFrame:
    """Liste les activités proposées dans une ville, de la moins chère à la plus chère."""
    return query(conn, SQL_ACTIVITES, (ville,))
