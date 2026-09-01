import pytest

from src import queries
from src.database import build_database


@pytest.fixture()
def conn():
    connection = build_database()
    yield connection
    connection.close()


def test_flights_from_origin(conn):
    result = queries.flights_from_origin(conn, "Nice")
    assert len(result) == 13
    assert list(result.columns) == ["flight_number", "destination", "departure_time", "price_eur"]


def test_cheap_flights(conn):
    result = queries.cheap_flights(conn, max_price=100)
    assert len(result) == 6
    assert result["price_eur"].is_monotonic_increasing


def test_passenger_search(conn):
    result = queries.passenger_search(conn, "Tanaka")
    assert len(result) == 1
    assert result.iloc[0]["first_name"] == "Yako"


def test_booking_status_breakdown(conn):
    result = queries.booking_status_breakdown(conn)
    assert len(result) == 3
    confirmed = result[result["status"] == "confirmed"]["count"].iloc[0]
    assert confirmed == 16


def test_revenue_by_destination_top_route(conn):
    result = queries.revenue_by_destination(conn)
    assert result["total_revenue"].is_monotonic_decreasing
    assert result.iloc[0]["destination"] == "New York JFK"


def test_recurring_demand_destinations(conn):
    result = queries.recurring_demand_destinations(conn, min_bookings=1)
    assert all(result["nb_bookings"] > 1)


def test_passengers_on_flight(conn):
    result = queries.passengers_on_flight(conn, "AF5501")
    assert len(result) == 4
    assert set(result["last_name"]) == {"Bernard", "Thomas", "Tanaka", "Smith"}


def test_passengers_never_booked(conn):
    result = queries.passengers_never_booked(conn)
    assert len(result) == 1


def test_above_average_price_flights(conn):
    result = queries.above_average_price_flights(conn)
    avg_price = conn.execute("SELECT AVG(price_eur) FROM flights").fetchone()[0]
    assert all(result["price_eur"] > avg_price)


def test_loyal_passengers(conn):
    result = queries.loyal_passengers(conn, min_bookings=2)
    assert len(result) == 5
    assert all(result["nb_bookings"] >= 2)
