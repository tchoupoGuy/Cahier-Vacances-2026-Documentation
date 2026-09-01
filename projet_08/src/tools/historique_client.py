"""Outil : historique des commandes d'un client (SQL paramétré)."""

from __future__ import annotations

import psycopg

from src.data.database import query

SQL_HISTORIQUE = """
SELECT id, order_number, status, total_amount, currency, ordered_at
FROM orders
WHERE customer_id = %s
ORDER BY ordered_at DESC
"""


def historique_client(conn: psycopg.Connection, customer_id: int):
    """Liste les commandes passées par un client, la plus récente d'abord.

    Args:
        conn: connexion ouverte (voir src.data.database.connect).
        customer_id: identifiant du client (customers.id).

    Returns:
        DataFrame des commandes du client (vide si le client n'en a aucune).
    """
    return query(conn, SQL_HISTORIQUE, (customer_id,))
