"""Teste l'API FastAPI de bout en bout, sans réseau ni écriture dans la vraie base.

Deux doublures suffisent : un encodeur factice (comme pour `test_planner.py`)
injecté à la place du vrai modèle Hugging Face, et une connexion vers une
COPIE temporaire de `voyages.db` à la place de la vraie base. Le reste —
FastAPI, la validation Pydantic, les routes — tourne pour de vrai.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.main as api_main
from src.data.brochures import load_brochures
from src.data.database import connect
from tests.fakes import FakeEncoder

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_copy = tmp_path / "voyages.db"
    shutil.copy(DATA_DIR / "voyages.db", db_copy)

    # Pas de vrai modèle d'embeddings : un encodeur factice suffit à tester le
    # câblage HTTP. `default_encode` (dans planner.py/hotels.py) ne fait
    # qu'appeler `encoder.encode(...)`, donc lui passer un FakeEncoder — qui a
    # la même méthode `.encode()` — suffit à remplacer le vrai modèle de bout
    # en bout, sans toucher au code de production.
    monkeypatch.setattr(api_main, "load_encoder", lambda: FakeEncoder(["piscine", "famille"]))
    # Les vraies brochures PDF (135 hôtels) : aucun réseau requis, seulement du parsing.
    monkeypatch.setattr(api_main, "load_brochures", lambda: load_brochures(DATA_DIR / "hotels"))
    # Chaque requête doit utiliser la copie temporaire, jamais la vraie base.
    monkeypatch.setattr(api_main, "_connection", lambda: connect(db_copy))

    with TestClient(api_main.app) as test_client:
        yield test_client


def test_destinations_lists_known_cities(client):
    response = client.get("/api/destinations")
    assert response.status_code == 200
    destinations = response.json()["destinations"]
    assert "Madrid" in destinations
    assert destinations == sorted(destinations)


def test_plan_returns_a_trip_within_budget(client):
    demande = {
        "destination": "Madrid", "date_depart": "2026-08-12", "nuits": 4,
        "voyageurs": 2, "budget_max": 700, "envie": "piscine",
    }
    response = client.post("/api/plan", json=demande)
    assert response.status_code == 200
    body = response.json()
    assert body["voyage"] is not None
    assert body["voyage"]["prix_total"] <= 700
    assert body["voyage"]["destination"] == "Madrid"
    assert isinstance(body["journal"], list)
    assert body["description"]  # une phrase a bien été rédigée


def test_plan_rejects_invalid_payload(client):
    response = client.post("/api/plan", json={"destination": "Madrid"})  # champs manquants
    assert response.status_code == 422


def test_book_without_confirmation_does_not_reserve(client):
    plan = client.post("/api/plan", json={
        "destination": "Madrid", "date_depart": "2026-08-12", "nuits": 4,
        "voyageurs": 2, "budget_max": 700, "envie": "piscine",
    }).json()

    response = client.post("/api/book", json={
        "voyage": plan["voyage"], "client": "Marc", "confirme": False,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["reserve"] is False
    assert "Rien n'a été réservé" in body["message"]


def test_book_with_confirmation_reserves(client):
    plan = client.post("/api/plan", json={
        "destination": "Madrid", "date_depart": "2026-08-12", "nuits": 4,
        "voyageurs": 2, "budget_max": 700, "envie": "piscine",
    }).json()

    response = client.post("/api/book", json={
        "voyage": plan["voyage"], "client": "Marc", "confirme": True,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["reserve"] is True
    assert "réservé" in body["message"].lower()
