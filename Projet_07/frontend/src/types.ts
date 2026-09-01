/**
 * Miroir exact de `api/schemas.py`. Un champ ajouté côté Python sans son
 * équivalent ici casse le typage silencieusement — garder les deux fichiers
 * synchronisés est la règle de ce module (voir le commentaire en tête de
 * `api/schemas.py`).
 */

export interface PlanRequest {
  destination: string;
  date_depart: string; // format AAAA-MM-JJ
  nuits: number;
  voyageurs: number;
  budget_max: number;
  envie: string;
}

export interface FlightOut {
  numero: string;
  origine: string;
  heure_depart: string;
  duree_h: number;
  prix_eur: number;
  places_restantes: number;
}

export interface HotelOut {
  hotel: string;
  ville: string;
  etoiles: number;
  prix_nuit: number;
  note: number;
  avis: number;
  resume: string;
  score: number;
}

export interface ActivityOut {
  nom: string;
  categorie: string;
  duree_h: number;
  prix_eur: number;
}

export interface TripOut {
  destination: string;
  date_depart: string;
  nuits: number;
  voyageurs: number;
  vol: FlightOut;
  hotel: HotelOut;
  activites: ActivityOut[];
  prix_total: number;
  budget_max: number;
}

export interface PlanResponse {
  voyage: TripOut | null;
  journal: string[];
  description: string;
}

export interface BookRequest {
  voyage: TripOut;
  client: string;
  confirme: boolean;
}

export interface BookResponse {
  message: string;
  reserve: boolean;
}

export interface DestinationsResponse {
  destinations: string[];
}
