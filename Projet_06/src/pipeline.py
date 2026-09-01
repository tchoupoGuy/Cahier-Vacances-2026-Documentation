"""Pipeline complet : du carnet de ventes brut à la comparaison des modèles et la prévision."""

from __future__ import annotations

from pathlib import Path

from src.baseline.naive import baseline_mean, baseline_yesterday
from src.data.loader import load_sales, train_test_split_series
from src.evaluation.diagnostics import ljung_box_pvalue
from src.evaluation.metrics import mae, scores_table
from src.models.arima_models import fit_arma, fit_ma, one_day_ahead_forecast

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "ventes_glaces.csv"

N_TEST = 22
MA_ORDER = 3
ARMA_ORDER = (1, 1)


def run_pipeline(data_path: Path = DATA_PATH, n_test: int = N_TEST) -> dict:
    df = load_sales(data_path)
    ventes = df["ventes"].to_numpy(dtype=float)
    dates = df["date"]

    train, test, dates_test = train_test_split_series(ventes, dates, n_test)

    scores = {
        "Toujours la moyenne": mae(test, baseline_mean(train, n_test)),
        "Comme hier": mae(test, baseline_yesterday(ventes, n_test)),
    }

    ma_result = fit_ma(train, q=MA_ORDER)
    scores[f"MA({MA_ORDER}), train seul"] = mae(test, one_day_ahead_forecast(ma_result, ventes, n_test))

    # Réentraînés sur tout l'historique disponible (hors les n_test derniers jours de test)
    ma_full = fit_ma(ventes[:-n_test], q=MA_ORDER)
    arma_full = fit_arma(ventes[:-n_test], p=ARMA_ORDER[0], q=ARMA_ORDER[1])

    scores[f"MA({MA_ORDER}), historique complet"] = mae(test, one_day_ahead_forecast(ma_full, ventes, n_test))
    scores[f"ARMA{ARMA_ORDER}, historique complet"] = mae(test, one_day_ahead_forecast(arma_full, ventes, n_test))

    diagnostics = {
        f"MA({MA_ORDER})": ljung_box_pvalue(ma_full),
        f"ARMA{ARMA_ORDER}": ljung_box_pvalue(arma_full),
    }

    return {
        "df": df,
        "train": train,
        "test": test,
        "dates_test": dates_test,
        "ma_result": ma_full,
        "arma_result": arma_full,
        "scores": scores,
        "scores_table": scores_table(scores),
        "diagnostics": diagnostics,
    }
