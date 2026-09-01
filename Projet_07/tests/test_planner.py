"""Teste la boucle de décision de l'agent avec des données contrôlées.

Les vols et activités viennent de la vraie base (Madrid, 12 août 2026 :
vol le moins cher 124 EUR, activités payantes 6+14+15+15+35+45 = 130 EUR).
Les hôtels sont volontairement synthétiques (2 hôtels), pour maîtriser
exactement à quel budget chaque repli doit se déclencher.
"""

import pandas as pd

from src.agent.planner import plan_trip, try_one_date
from tests.fakes import FakeEncoder, fake_encode

HOTELS_MADRID = pd.DataFrame([
    {"ville": "Madrid", "hotel": "Hotel Familia", "prix_nuit": 100.0, "etoiles": 4,
     "note": 8.5, "avis": 120, "texte": "hotel pour la famille avec piscine",
     "resume": "hotel pour la famille avec piscine"},
    {"ville": "Madrid", "hotel": "Hotel Economico", "prix_nuit": 40.0, "etoiles": 2,
     "note": 7.0, "avis": 30, "texte": "hotel simple au centre ville",
     "resume": "hotel simple au centre ville"},
])
VOCABULARY = ["piscine", "famille"]
ENCODER = FakeEncoder(VOCABULARY)

DEMANDE_BASE = {
    "destination": "Madrid", "date_depart": "2026-08-12", "nuits": 4, "voyageurs": 2,
    "envie": "piscine",
}


def _demande(budget):
    return dict(DEMANDE_BASE, budget_max=budget)


def test_fits_within_budget_without_any_sacrifice(conn):
    voyage, journal = try_one_date(_demande(700), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is not None
    assert voyage["prix_total"] <= 700
    assert voyage["hotel"]["hotel"] == "Hotel Familia"
    assert journal == []


def test_sacrifices_activities_before_touching_the_hotel(conn):
    voyage, journal = try_one_date(_demande(600), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is not None
    assert voyage["hotel"]["hotel"] == "Hotel Familia"  # pas encore de repli hôtel
    assert voyage["prix_total"] <= 600
    assert len(journal) == 2  # les deux sorties les plus chères (45 et 35 EUR) retirées
    assert all("à la place" not in ligne for ligne in journal)


def test_never_sacrifices_a_free_activity(conn):
    voyage, journal = try_one_date(_demande(600), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    noms_gardes = [a["nom"] for a in voyage["activites"]]
    gratuites = ["Parc du Retiro", "Temple de Debod"]
    assert all(nom in noms_gardes for nom in gratuites)


def test_falls_back_to_cheaper_hotel_once_activities_are_exhausted(conn):
    voyage, journal = try_one_date(_demande(450), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is not None
    assert voyage["hotel"]["hotel"] == "Hotel Economico"
    assert voyage["prix_total"] <= 450
    assert any("à la place" in ligne for ligne in journal)


def test_gives_up_when_nothing_fits(conn):
    voyage, journal = try_one_date(_demande(200), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is None
    assert "plus rien à sacrifier" in journal[-1]


def test_plan_trip_never_moves_the_requested_date(conn):
    voyage, journal = plan_trip(_demande(700), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is not None
    assert voyage["date_depart"] == "2026-08-12"  # jamais déplacée automatiquement
    assert isinstance(journal, list)


def test_plan_trip_signals_a_cheaper_neighbouring_day_when_impossible_today(conn):
    # 250 EUR est infaisable le 12 (minimum 124 + 160 = 284 EUR), mais le 11 août le vol
    # le moins cher tombe à 89 EUR : 89 + 160 = 249 EUR, tout juste sous ce budget serré.
    voyage, journal = plan_trip(_demande(250), conn, HOTELS_MADRID, ENCODER, encode_fn=fake_encode)
    assert voyage is None
    assert any("devenait possible" in ligne for ligne in journal)
