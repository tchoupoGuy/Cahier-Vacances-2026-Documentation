import pandas as pd

from src.agent.pricing import neighbouring_dates, price_trip


def test_price_trip_sums_flight_hotel_and_activities():
    vol = pd.Series({"prix_eur": 100.0})
    hotel = pd.Series({"prix_nuit": 50.0})
    activites = [{"prix_eur": 20.0}, {"prix_eur": 0.0}]

    total = price_trip(vol, hotel, activites, nuits=4)

    assert total == 100.0 + 50.0 * 4 + 20.0


def test_price_trip_with_no_activities():
    vol = pd.Series({"prix_eur": 100.0})
    hotel = pd.Series({"prix_nuit": 50.0})
    assert price_trip(vol, hotel, [], nuits=2) == 200.0


def test_neighbouring_dates_excludes_the_requested_date():
    voisines = neighbouring_dates("2026-08-12", ecart=2)
    assert "2026-08-12" not in voisines
    assert set(voisines) == {"2026-08-11", "2026-08-13", "2026-08-10", "2026-08-14"}
