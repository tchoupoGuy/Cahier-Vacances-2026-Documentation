"""Construction de la base de données SQLite du système de réservations.

Sépare la responsabilité "architecture des données" (sql/schema.sql,
sql/seed.sql) du code Python, qui se contente d'exécuter ces scripts.
C'est le pattern habituel en entreprise : le schéma et les migrations
vivent dans des fichiers .sql versionnés, pas dans des chaînes Python.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
SCHEMA_FILE = SQL_DIR / "schema.sql"
SEED_FILE = SQL_DIR / "seed.sql"


def build_database(*, in_memory: bool = True, db_path: str | Path = ":memory:") -> sqlite3.Connection:
    """Crée une connexion SQLite, applique le schéma puis les données de départ.

    Parameters
    ----------
    in_memory:
        Si True (par défaut), la base vit uniquement en RAM le temps de la
        session, comme dans le notebook d'origine.
    db_path:
        Chemin du fichier si `in_memory=False`.
    """
    target = ":memory:" if in_memory else str(db_path)
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    conn.executescript(SEED_FILE.read_text(encoding="utf-8"))
    conn.commit()

    return conn


def table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Petit contrôle de cohérence : nombre de lignes par table."""
    counts = {}
    for table in ("passengers", "flights", "bookings"):
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return counts
