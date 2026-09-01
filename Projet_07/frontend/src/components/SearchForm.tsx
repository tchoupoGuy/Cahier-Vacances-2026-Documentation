import { useEffect, useState } from "react";
import { getDestinations } from "../api";
import type { PlanRequest } from "../types";

interface SearchFormProps {
  onSubmit: (demande: PlanRequest) => void;
  loading: boolean;
}

const DEFAULT_DEMANDE: PlanRequest = {
  destination: "",
  date_depart: "2026-08-12",
  nuits: 4,
  voyageurs: 2,
  budget_max: 750,
  envie: "un hôtel pour la famille avec une piscine, et des visites dans la ville",
};

/** Le formulaire de recherche : mêmes 6 clés que `demande` côté agent Python. */
export function SearchForm({ onSubmit, loading }: SearchFormProps) {
  const [demande, setDemande] = useState<PlanRequest>(DEFAULT_DEMANDE);
  const [destinations, setDestinations] = useState<string[]>([]);
  const [destinationsError, setDestinationsError] = useState<string | null>(null);

  useEffect(() => {
    getDestinations()
      .then((res) => setDestinations(res.destinations))
      .catch((err) => setDestinationsError(err.message));
  }, []);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    onSubmit(demande);
  }

  function update<K extends keyof PlanRequest>(key: K, value: PlanRequest[K]) {
    setDemande((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="destination">Destination</label>
        {destinations.length > 0 ? (
          <select
            id="destination"
            required
            value={demande.destination}
            onChange={(e) => update("destination", e.target.value)}
          >
            <option value="" disabled>
              Choisir une ville
            </option>
            {destinations.map((ville) => (
              <option key={ville} value={ville}>
                {ville}
              </option>
            ))}
          </select>
        ) : (
          <input
            id="destination"
            required
            placeholder={destinationsError ? "ex: Madrid" : "Chargement..."}
            value={demande.destination}
            onChange={(e) => update("destination", e.target.value)}
          />
        )}
        {destinationsError && (
          <p className="field-hint">Liste des destinations indisponible : {destinationsError}</p>
        )}
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="date_depart">Date de départ</label>
          <input
            id="date_depart"
            type="date"
            required
            value={demande.date_depart}
            onChange={(e) => update("date_depart", e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="nuits">Nuits</label>
          <input
            id="nuits"
            type="number"
            min={1}
            required
            value={demande.nuits}
            onChange={(e) => update("nuits", Number(e.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="voyageurs">Voyageurs</label>
          <input
            id="voyageurs"
            type="number"
            min={1}
            required
            value={demande.voyageurs}
            onChange={(e) => update("voyageurs", Number(e.target.value))}
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="budget_max">Budget max (par personne, en EUR)</label>
        <input
          id="budget_max"
          type="number"
          min={1}
          required
          value={demande.budget_max}
          onChange={(e) => update("budget_max", Number(e.target.value))}
        />
      </div>

      <div className="field">
        <label htmlFor="envie">Ce que vous cherchez</label>
        <textarea
          id="envie"
          required
          rows={2}
          value={demande.envie}
          onChange={(e) => update("envie", e.target.value)}
        />
      </div>

      <button type="submit" disabled={loading || !demande.destination}>
        {loading ? "L'agent réfléchit..." : "Planifier le voyage"}
      </button>
    </form>
  );
}
