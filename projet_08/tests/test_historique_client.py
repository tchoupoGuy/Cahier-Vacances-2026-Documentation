from src.tools.historique_client import historique_client


def test_lists_orders_most_recent_first(conn):
    # Client 1 (seed.sql) a 2 commandes : ORD-2026-0001 (1er juillet) et
    # ORD-2026-0002 (5 août) — la plus récente doit sortir en premier.
    resultat = historique_client(conn, 1)

    assert list(resultat["order_number"]) == ["ORD-2026-0002", "ORD-2026-0001"]


def test_empty_when_customer_has_no_orders(conn):
    resultat = historique_client(conn, 9999)  # aucun client 9999 dans seed.sql

    assert resultat.empty
