"""API FastAPI de l'agent de voyage.

Expose `src/` (l'agent) en HTTP JSON pour le frontend React/TypeScript, sans
dupliquer la moindre logique métier : cette couche ne fait que
(1) valider l'entrée, (2) appeler `src/`, (3) reformater la sortie.

Lancer :
    uvicorn api.main:app --reload --port 8000

Le vrai modèle d'embeddings (Hugging Face) est chargé une seule fois au
démarrage, comme le ferait `st.cache_resource` côté Streamlit — sans quoi
chaque requête rechargerait ~500 Mo de modèle.
"""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.converters import trip_to_dict
from api.schemas import (
    BookRequest,
    BookResponse,
    DestinationsResponse,
    PlanRequest,
    PlanResponse,
)
from src.agent.booking import book_trip
from src.agent.planner import plan_trip
from src.data.brochures import load_brochures
from src.data.database import DEFAULT_DB_PATH, connect, query
from src.display import trip_description
from src.embeddings.encoder import load_encoder

# Chargé une fois au démarrage, réutilisé par toutes les requêtes (lecture seule).
_cache: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _cache["brochures"] = load_brochures()
    _cache["encoder"] = load_encoder()
    yield
    _cache.clear()


app = FastAPI(title="Agent de voyage — API", lifespan=lifespan)

# Le serveur de développement Vite tourne par défaut sur le port 5173, mais
# en prend un autre (5174, 5175...) si celui-ci est déjà occupé : on autorise
# donc tout port localhost/127.0.0.1, plutôt qu'un seul port figé qui casse
# le CORS ("Disallowed CORS origin") dès que Vite en choisit un autre.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _connection() -> sqlite3.Connection:
    """Une connexion PAR REQUÊTE : sqlite3 n'est pas conçu pour être partagé entre threads,
    et FastAPI exécute les endpoints synchrones dans un pool de threads.
    """
    return connect(DEFAULT_DB_PATH)


@app.get("/api/destinations", response_model=DestinationsResponse)
def get_destinations() -> DestinationsResponse:
    """Les destinations desservies, pour peupler le formulaire de recherche."""
    conn = _connection()
    try:
        df = query(conn, "SELECT DISTINCT destination FROM vols ORDER BY destination")
    finally:
        conn.close()
    return DestinationsResponse(destinations=df["destination"].tolist())


@app.post("/api/plan", response_model=PlanResponse)
def post_plan(demande: PlanRequest) -> PlanResponse:
    """Demande à l'agent de composer un voyage : mêmes appels que `main.py`, en HTTP."""
    conn = _connection()
    try:
        voyage, journal = plan_trip(
            demande.model_dump(), conn, _cache["brochures"], _cache["encoder"],
        )
    finally:
        conn.close()

    return PlanResponse(
        voyage=trip_to_dict(voyage) if voyage is not None else None,
        journal=journal,
        description=trip_description(voyage, journal),
    )


@app.post("/api/book", response_model=BookResponse)
def post_book(reservation: BookRequest) -> BookResponse:
    """Réserve (ou décrit ce que ferait la réservation, si `confirme=False`).

    Sans état côté serveur : le client renvoie le voyage complet qu'il a reçu
    de `/api/plan`. `book_trip` ne lit que les clés dont il a besoin, donc un
    dict issu de `TripOut.model_dump()` lui convient tout autant qu'un
    `pandas.Series` — c'est la même logique que celle testée dans
    `tests/test_booking.py`.
    """
    conn = _connection()
    try:
        voyage = reservation.voyage.model_dump()
        message = book_trip(conn, voyage, reservation.client, confirme=reservation.confirme)
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()

    return BookResponse(message=message, reserve=reservation.confirme)
