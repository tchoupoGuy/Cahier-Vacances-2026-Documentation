import type {
  BookRequest,
  BookResponse,
  DestinationsResponse,
  PlanRequest,
  PlanResponse,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** Erreur levée quand l'API répond avec un statut d'échec (4xx/5xx). */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(0, "Impossible de joindre l'API. Est-elle bien lancée (uvicorn api.main:app) ?");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message = typeof detail === "string" ? detail : `Erreur API (${response.status})`;
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

export function getDestinations(): Promise<DestinationsResponse> {
  return request<DestinationsResponse>("/api/destinations");
}

export function planTrip(demande: PlanRequest): Promise<PlanResponse> {
  return request<PlanResponse>("/api/plan", {
    method: "POST",
    body: JSON.stringify(demande),
  });
}

export function bookTrip(reservation: BookRequest): Promise<BookResponse> {
  return request<BookResponse>("/api/book", {
    method: "POST",
    body: JSON.stringify(reservation),
  });
}
