"""Point d'entrée : compare les modèles et prévoit la semaine prochaine pour Bruno.

Usage :
    python main.py
"""

from __future__ import annotations

from pathlib import Path

from src.models.arima_models import forecast_next_days
from src.pipeline import run_pipeline
from src.visualization.plots import plot_correlograms, plot_sales, plot_week_ahead

FIGURES_DIR = Path(__file__).resolve().parent / "reports" / "figures"


def main() -> None:
    result = run_pipeline()

    print(result["scores_table"].to_string(index=False))
    print()
    for name, pvalue in result["diagnostics"].items():
        verdict = "bruit pur, rien oublié" if pvalue > 0.05 else "il reste de la structure non captée !"
        print(f"{name:12s} Ljung-Box p = {pvalue:.3f}  -> {verdict}")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_sales(result["df"], FIGURES_DIR / "sales.png")
    plot_correlograms(result["train"], FIGURES_DIR / "correlograms.png", lags=20, title="- historique complet")

    mean_forecast, _ = forecast_next_days(result["arma_result"], steps=7)
    print(f"\nPrévision des 7 prochains jours (ARMA) : {[round(v, 1) for v in mean_forecast]}")

    plot_week_ahead(result["train"], result["arma_result"], FIGURES_DIR / "week_ahead.png")


if __name__ == "__main__":
    main()
