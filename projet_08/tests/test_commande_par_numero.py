from src.tools.commande_par_numero import commande_par_numero


def test_finds_the_right_order(conn):
    resultat = commande_par_numero(conn, "ORD-2026-0003")

    assert len(resultat) == 1
    ligne = resultat.iloc[0]
    assert ligne["customer_id"] == 2
    assert ligne["status"] == "delivered"
    # 9996 = 3999 + 3 x 1999, la valeur corrigée pour correspondre aux order_items (voir sql/seed.sql).
    assert ligne["total_amount"] == 9996


def test_empty_for_unknown_order_number(conn):
    resultat = commande_par_numero(conn, "ORD-2026-9999")

    assert resultat.empty
