"""Ajustement des modèles MA et ARMA (implémentés via ARIMA(p, d, q) de statsmodels)."""

from __future__ import annotations

import numpy as np


def fit_ma(train: np.ndarray, q: int = 3):
    """Ajuste un MA(q) pur : order=(0, 0, q), avec une constante estimée."""
    from statsmodels.tsa.arima.model import ARIMA

    return ARIMA(train, order=(0, 0, q), trend="c").fit()


def fit_arma(train: np.ndarray, p: int = 1, q: int = 1):
    """Ajuste un ARMA(p, q) : order=(p, 0, q), avec une constante estimée."""
    from statsmodels.tsa.arima.model import ARIMA

    return ARIMA(train, order=(p, 0, q), trend="c").fit()


def one_day_ahead_forecast(fitted_result, full_series: np.ndarray, n_test: int) -> np.ndarray:
    """Prévoit chaque jour de test, un jour à l'avance, sans réestimer les coefficients.

    Chaque soir, le modèle regarde tout ce qui a été observé jusque-là et
    prédit demain : les coefficients restent ceux appris sur le train, seule
    la fenêtre d'observations avance.
    """
    applied = fitted_result.apply(np.asarray(full_series, dtype=float))
    return applied.get_prediction(start=len(full_series) - n_test).predicted_mean


def forecast_next_days(fitted_result, steps: int = 7):
    """Prolonge la série de `steps` jours dans le futur (prévision moyenne + intervalle)."""
    forecast = fitted_result.get_forecast(steps=steps)
    return forecast.predicted_mean, forecast.conf_int()
