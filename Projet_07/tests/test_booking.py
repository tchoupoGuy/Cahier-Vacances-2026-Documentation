import pandas as pd

from src.agent.booking import book_trip
from src.data.database import query

VOYAGE = {
    "destination": "Madrid", "date_depart": "2026-08-12", "nuits": 4, "voyageurs": 2,
    "vol": pd.Series({"numero": "W65397", "prix_eur": 124.0}),
    "hotel": pd.Series({"hotel": "Hotel Familia", "prix_nuit": 100.0}),
    "activites": [{"nom": "Musée du Prado", "prix_eur": 15.0}],
    "prix_total": 539.0, "budget_max": 600.0,
}


def _count_reservations(conn):
    return len(query(conn, "SELECT * FROM reservations"))


def test_booking_without_confirmation_writes_nothing(conn):
    avant = _count_reservations(conn)
    message = book_trip(conn, VOYAGE, "Marc", confirme=False)
    apres = _count_reservations(conn)

    assert apres == avant
    assert "Rien n'a été réservé" in message


def test_booking_with_confirmation_writes_one_row(conn):
    avant = _count_reservations(conn)
    message = book_trip(conn, VOYAGE, "Marc", confirme=True)
    apres = _count_reservations(conn)

    assert apres == avant + 1
    assert "réservé" in message.lower()


def test_booking_with_no_trip_does_not_crash(conn):
    message = book_trip(conn, None, "Marc", confirme=True)
    assert "Rien à réserver" in message
