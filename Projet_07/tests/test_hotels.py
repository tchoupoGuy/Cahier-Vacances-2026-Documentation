import pandas as pd

from src.tools.hotels import find_hotels
from tests.fakes import FakeEncoder, fake_encode

SYNTHETIC_BROCHURES = pd.DataFrame([
    {"ville": "Madrid", "hotel": "Hotel Famille", "resume": "Un hotel ideal pour la famille avec des enfants."},
    {"ville": "Madrid", "hotel": "Hotel Piscine", "resume": "Une grande piscine pour nager toute la journee."},
    {"ville": "Madrid", "hotel": "Hotel Fete", "resume": "Ambiance festive, sortir le soir en boite."},
    {"ville": "Rome", "hotel": "Autre Ville", "resume": "Un hotel a Rome, sans rapport avec la recherche."},
])
VOCABULARY = ["famille", "enfants", "piscine", "fete", "boite"]


def test_find_hotels_filters_by_city():
    results = find_hotels(SYNTHETIC_BROCHURES, FakeEncoder(VOCABULARY), "Madrid", "piscine", k=3,
                           encode_fn=fake_encode)
    assert set(results["ville"]) == {"Madrid"}


def test_find_hotels_ranks_matching_hotel_first():
    results = find_hotels(SYNTHETIC_BROCHURES, FakeEncoder(VOCABULARY), "Madrid",
                           "en famille avec des enfants", k=3, encode_fn=fake_encode)
    assert results.iloc[0]["hotel"] == "Hotel Famille"
    assert results["score"].is_monotonic_decreasing


def test_find_hotels_respects_k():
    results = find_hotels(SYNTHETIC_BROCHURES, FakeEncoder(VOCABULARY), "Madrid", "piscine", k=2,
                           encode_fn=fake_encode)
    assert len(results) == 2
