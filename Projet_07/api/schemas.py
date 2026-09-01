"""Schémas Pydantic : le contrat entre l'API et le frontend TypeScript.

Chaque modèle a son miroir exact côté TypeScript dans `frontend/src/types.ts`.
Garder les deux fichiers synchronisés est LA règle de ce module : un champ
ajouté ici sans son équivalent côté frontend casse le typage silencieusement
(TypeScript ne peut pas savoir que l'API a changé de forme).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Ce que le formulaire de recherche du frontend envoie."""

    destination: str
    date_depart: str = Field(description="format AAAA-MM-JJ, ex: 2026-08-12")
    nuits: int = Field(gt=0)
    voyageurs: int = Field(gt=0)
    budget_max: float = Field(gt=0)
    envie: str = Field(description="ce que le voyageur cherche, en langage libre")


class FlightOut(BaseModel):
    numero: str
    origine: str
    heure_depart: str
    duree_h: float
    prix_eur: float
    places_restantes: int


class HotelOut(BaseModel):
    hotel: str
    ville: str
    etoiles: int
    prix_nuit: float
    note: float
    avis: int
    resume: str
    score: float


class ActivityOut(BaseModel):
    nom: str
    categorie: str
    duree_h: float
    prix_eur: float


class TripOut(BaseModel):
    """Le voyage composé par l'agent, tel qu'affiché par `print_trip` en CLI."""

    destination: str
    date_depart: str
    nuits: int
    voyageurs: int
    vol: FlightOut
    hotel: HotelOut
    activites: list[ActivityOut]
    prix_total: float
    budget_max: float


class PlanResponse(BaseModel):
    """Ce que /api/plan renvoie : le voyage demandé (ou rien) + le journal de l'agent."""

    voyage: TripOut | None
    journal: list[str]
    description: str


class BookRequest(BaseModel):
    """Le client renvoie le voyage complet reçu de /api/plan : l'API ne garde aucun état."""

    voyage: TripOut
    client: str
    confirme: bool = False


class BookResponse(BaseModel):
    message: str
    reserve: bool


class DestinationsResponse(BaseModel):
    destinations: list[str]
