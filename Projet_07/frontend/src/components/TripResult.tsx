import type { PlanResponse } from "../types";

interface TripResultProps {
  result: PlanResponse;
}

/** Affiche le voyage composé par l'agent + le journal de ses décisions.
 *  Équivalent React de `src/display.py::print_trip` côté CLI. */
export function TripResult({ result }: TripResultProps) {
  const { voyage, journal, description } = result;

  if (voyage === null) {
    return (
      <div className="trip-result trip-result--empty">
        <p>Aucun voyage ne rentre dans ce budget.</p>
        {journal.length > 0 && (
          <ul className="journal">
            {journal.map((ligne, i) => (
              <li key={i}>{ligne}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div className="trip-result">
      <h2>
        {voyage.destination} — {voyage.nuits} nuits, {voyage.voyageurs} voyageur(s)
      </h2>

      <div className="trip-line">
        <span className="trip-line__label">Vol</span>
        <span>
          {voyage.vol.numero} depuis {voyage.vol.origine}, le {voyage.date_depart} à{" "}
          {voyage.vol.heure_depart} ({voyage.vol.duree_h.toFixed(0)} h) —{" "}
          {voyage.vol.prix_eur.toFixed(0)} EUR/pers
        </span>
      </div>

      <div className="trip-line">
        <span className="trip-line__label">Hôtel</span>
        <span>
          {voyage.hotel.hotel} ({voyage.hotel.etoiles}★, note {voyage.hotel.note.toFixed(1)}/10) —{" "}
          {voyage.hotel.prix_nuit.toFixed(0)} EUR/nuit, soit{" "}
          {(voyage.hotel.prix_nuit * voyage.nuits).toFixed(0)} EUR
        </span>
      </div>

      <div className="trip-line trip-line--activities">
        <span className="trip-line__label">Activités</span>
        {voyage.activites.length === 0 ? (
          <span>aucune</span>
        ) : (
          <ul>
            {voyage.activites.map((a) => (
              <li key={a.nom}>
                {a.nom} — {a.prix_eur === 0 ? "gratuit" : `${a.prix_eur.toFixed(0)} EUR`}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="trip-total">
        <strong>TOTAL {voyage.prix_total.toFixed(0)} EUR</strong> / pers (budget :{" "}
        {voyage.budget_max.toFixed(0)} EUR)
      </div>

      <p className="trip-description">{description}</p>

      {journal.length > 0 && (
        <details className="journal-details">
          <summary>Ce que l'agent a fait ({journal.length})</summary>
          <ul className="journal">
            {journal.map((ligne, i) => (
              <li key={i}>{ligne}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
