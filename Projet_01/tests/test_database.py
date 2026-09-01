import pytest

from src.database import build_database, table_counts


@pytest.fixture()
def conn():
    connection = build_database()
    yield connection
    connection.close()


def test_table_counts(conn):
    counts = table_counts(conn)
    assert counts == {"passengers": 15, "flights": 15, "bookings": 19}


def test_seat_class_check_constraint(conn):
    with pytest.raises(Exception):
        conn.execute(
            "INSERT INTO bookings VALUES (999, 1, 1, '2026-06-30', 'premium', '1A', 'confirmed')"
        )
