"""Accès à la base de données des voyages (vols, activités, réservations)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "voyages.db"


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Ouvre la base de données des voyages."""
    return sqlite3.connect(str(db_path))


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    """Exécute une requête SQL PARAMÉTRÉE et renvoie le résultat en DataFrame.

    Les valeurs ne sont jamais collées dans le texte de la requête (pas de
    f-string) : elles passent par des `?`, remplis dans l'ordre par `params`.
    C'est ce qui protège des injections SQL et des caractères spéciaux
    (une apostrophe dans un nom de ville, par exemple).
    """
    return pd.read_sql_query(sql, conn, params=params)
