"""Outil : retrouver une commande à partir de son numéro (SQL paramétré)."""

from __future__ import annotations

import pandas as pd
import psycopg

from src.data.database import query

SQL_COMMANDE = """
SELECT id, customer_id, order_number, status, total_amount, currency,
       shipping_address, ordered_at
FROM orders
WHERE order_number = %s
"""


def commande_par_numero(conn: psycopg.Connection, order_number: str) -> pd.DataFrame:
    """Retrouve une commande à partir du numéro donné par le client.

    Args:
        conn: connexion ouverte (voir src.data.database.connect).
        order_number: le numéro de commande tel que le client le fournit
            (ex. "ORD-2026-0003"), pas l'id interne.

    Returns:
        DataFrame d'au plus une ligne (order_number est UNIQUE dans le
        schéma) ; vide si aucune commande ne porte ce numéro.
    """
    return query(conn, SQL_COMMANDE, (order_number,))
