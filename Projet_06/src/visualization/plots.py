"""Graphiques : ventes brutes, corrélogrammes, prévisions, semaine à venir."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_sales(df: pd.DataFrame, out_path: Path, title: str = "Ventes quotidiennes de glaces") -> None:
    plt.figure(figsize=(13, 4))
    for saison, groupe in df.groupby("saison"):
        plt.plot(groupe["date"], groupe["ventes"], linewidth=1, label=f"été {saison}")
    plt.axhline(df["ventes"].mean(), color="black", linestyle="--", linewidth=1,
                label=f"moyenne ({df['ventes'].mean():.0f})")
    plt.ylabel("Glaces vendues")
    plt.title(title)
    plt.legend(ncol=5, fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_correlograms(serie, out_path: Path, lags: int = 15, title: str = "") -> None:
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    plot_acf(np.asarray(serie, dtype=float), lags=lags, ax=axes[0])
    axes[0].set_title(f"ACF {title}".strip())
    plot_pacf(np.asarray(serie, dtype=float), lags=lags, ax=axes[1], method="ywm")
    axes[1].set_title(f"PACF {title}".strip())
    for ax in axes:
        ax.set_xlabel("Retard (jours)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_forecasts(dates, real, forecasts: dict, out_path: Path, title: str = "Prévision à 1 jour") -> None:
    plt.figure(figsize=(13, 4.5))
    plt.plot(dates, real, color="black", marker="o", markersize=4, linewidth=2, label="ventes réelles")
    for name, values in forecasts.items():
        plt.plot(dates, values, marker=".", linewidth=1.2, alpha=0.9, label=name)
    plt.ylabel("Glaces vendues")
    plt.title(title)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_week_ahead(history, fitted_result, out_path: Path, steps: int = 7, days_shown: int = 40,
                     title: str = "La semaine du glacier") -> None:
    history = np.asarray(history, dtype=float)
    forecast = fitted_result.get_forecast(steps=steps)
    mean = np.asarray(forecast.predicted_mean, dtype=float)
    interval = np.asarray(forecast.conf_int(), dtype=float)

    past = np.arange(-days_shown, 0)
    future = np.arange(1, steps + 1)

    plt.figure(figsize=(11, 4.5))
    plt.plot(past, history[-days_shown:], color="black", linewidth=1.5, label="ventes observées")
    plt.plot(future, mean, color="crimson", marker="o", linewidth=2, label="prévision")
    plt.fill_between(future, interval[:, 0], interval[:, 1], color="crimson", alpha=0.15,
                      label="intervalle de confiance 95 %")
    plt.axhline(history.mean(), color="grey", linestyle="--", linewidth=1, label="moyenne historique")
    plt.axvline(0, color="grey", linewidth=0.8)
    plt.xlabel("Jours (0 = aujourd'hui)")
    plt.ylabel("Glaces vendues")
    plt.title(title)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
