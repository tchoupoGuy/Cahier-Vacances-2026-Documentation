import { useState } from "react";
import { ApiError, planTrip } from "./api";
import { BookingPanel } from "./components/BookingPanel";
import { SearchForm } from "./components/SearchForm";
import { TripResult } from "./components/TripResult";
import type { PlanRequest, PlanResponse } from "./types";
import "./App.css";

/** Page unique : formulaire -> résultat de l'agent -> réservation.
 *  Toute la logique (boucle de repli, garde-fou de réservation) vit dans
 *  l'API ; ce composant ne fait qu'appeler /api/plan puis /api/book. */
export default function App() {
  const [result, setResult] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(demande: PlanRequest) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await planTrip(demande);
      setResult(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Agent de voyage</h1>
        <p className="subtitle">
          Projet 07 — même agent que <code>main.py</code> et l'app Streamlit, servi ici par une API
          FastAPI à un frontend React + TypeScript.
        </p>
      </header>

      <SearchForm onSubmit={handleSearch} loading={loading} />

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <TripResult result={result} />
          {result.voyage && <BookingPanel voyage={result.voyage} />}
        </>
      )}
    </div>
  );
}
