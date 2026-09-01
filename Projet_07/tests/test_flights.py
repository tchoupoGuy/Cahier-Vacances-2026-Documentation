from src.tools.flights import find_flights


def test_find_flights_returns_expected_columns(conn):
    vols = find_flights(conn, "Madrid", "2026-08-12", voyageurs=2)
    assert not vols.empty
    assert list(vols.columns) == ["numero", "origine", "heure_depart", "duree_h", "prix_eur", "places_restantes"]


def test_find_flights_sorted_by_price(conn):
    vols = find_flights(conn, "Madrid", "2026-08-12", voyageurs=2)
    assert vols["prix_eur"].is_monotonic_increasing


def test_find_flights_respects_seat_count(conn):
    vols = find_flights(conn, "Madrid", "2026-08-12", voyageurs=5)
    assert (vols["places_restantes"] >= 5).all()


def test_find_flights_empty_for_unknown_date(conn):
    vols = find_flights(conn, "Madrid", "1999-01-01", voyageurs=1)
    assert vols.empty


def test_find_flights_handles_apostrophe_safely(conn):
    # Ne doit jamais lever d'exception, même avec une valeur "dangereuse" pour une f-string SQL.
    vols = find_flights(conn, "L'Escala", "2026-08-12", voyageurs=1)
    assert vols.empty
