import { useState } from "react";
import { ApiError, bookTrip } from "../api";
import type { TripOut } from "../types";

interface BookingPanelProps {
  voyage: TripOut;
}

/** Le garde-fou côté UI : un premier clic prévisualise (confirme=false),
 *  la réservation réelle exige un second clic explicite — même principe
 *  que `src/agent/booking.py::book_trip`. */
export function BookingPanel({ voyage }: BookingPanelProps) {
  const [client, setClient] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [reserved, setReserved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleBook(confirme: boolean) {
    if (!client.trim()) {
      setError("Indiquez un nom pour réserver.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await bookTrip({ voyage, client, confirme });
      setMessage(response.message);
      setReserved(response.reserve);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="booking-panel">
      <h3>Réserver</h3>
      <div className="field">
        <label htmlFor="client">Nom du voyageur</label>
        <input
          id="client"
          value={client}
          onChange={(e) => setClient(e.target.value)}
          placeholder="ex: Marc"
          disabled={reserved}
        />
      </div>

      {!reserved && (
        <div className="booking-actions">
          <button type="button" onClick={() => handleBook(false)} disabled={loading}>
            Voir le prix total
          </button>
          <button type="button" className="primary" onClick={() => handleBook(true)} disabled={loading}>
            Confirmer la réservation
          </button>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {message && <p className={reserved ? "booking-success" : "booking-preview"}>{message}</p>}
    </div>
  );
}
