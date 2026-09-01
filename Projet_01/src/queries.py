"""Bibliothèque de requêtes : charge les fichiers .sql et les exécute.

Chaque fonction correspond à une question métier posée dans le projet
d'origine. Le SQL lui-même vit dans sql/queries/, cette couche Python
se contente de charger le bon fichier, de passer les paramètres et de
renvoyer un DataFrame pandas.
"""

from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

import pandas as pd

QUERIES_DIR = Path(__file__).resolve().parent.parent / "sql" / "queries"


@lru_cache(maxsize=None)
def _load(relative_path: str) -> str:
    return (QUERIES_DIR / relative_path).read_text(encoding="utf-8")


def run(conn: sqlite3.Connection, relative_path: str, params: dict | None = None) -> pd.DataFrame:
    """Exécute une requête nommée (chemin relatif à sql/queries/) et renvoie un DataFrame."""
    sql = _load(relative_path)
    return pd.read_sql_query(sql, conn, params=params or {})


# --- Requêtes de base -------------------------------------------------

def flights_from_origin(conn: sqlite3.Connection, origin: str) -> pd.DataFrame:
    return run(conn, "basic/flights_from_origin.sql", {"origin": origin})


def cheap_flights(conn: sqlite3.Connection, max_price: float = 100.0) -> pd.DataFrame:
    return run(conn, "basic/cheap_flights.sql", {"max_price": max_price})


def passenger_search(conn: sqlite3.Connection, last_name: str) -> pd.DataFrame:
    return run(conn, "basic/passenger_search.sql", {"last_name": last_name})


# --- Requêtes analytiques (l'étude business) ---------------------------

def booking_status_breakdown(conn: sqlite3.Connection) -> pd.DataFrame:
    return run(conn, "analytics/booking_status_breakdown.sql")


def revenue_by_destination(conn: sqlite3.Connection) -> pd.DataFrame:
    return run(conn, "analytics/revenue_by_destination.sql")


def recurring_demand_destinations(conn: sqlite3.Connection, min_bookings: int = 1) -> pd.DataFrame:
    return run(conn, "analytics/recurring_demand_destinations.sql", {"min_bookings": min_bookings})


def passengers_on_flight(conn: sqlite3.Connection, flight_number: str) -> pd.DataFrame:
    return run(conn, "analytics/passengers_on_flight.sql", {"flight_number": flight_number})


def passengers_never_booked(conn: sqlite3.Connection) -> pd.DataFrame:
    return run(conn, "analytics/passengers_never_booked.sql")


def above_average_price_flights(conn: sqlite3.Connection) -> pd.DataFrame:
    return run(conn, "analytics/above_average_price_flights.sql")


def loyal_passengers(conn: sqlite3.Connection, min_bookings: int = 2) -> pd.DataFrame:
    return run(conn, "analytics/loyal_passengers.sql", {"min_bookings": min_bookings})
