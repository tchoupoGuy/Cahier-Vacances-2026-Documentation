"""Affichage : fond de carte de la France, étapes colorées, tracé final.

Toute la "plomberie" graphique est isolée ici, séparée du raisonnement de
clustering et de routage. Le contour de la France (polygones) vit dans
data/france_outline.json, pas dans le code : c'est une donnée, pas de la logique.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

MAP_ASPECT_RATIO = 1.4
STAGE_COLORS = list(plt.get_cmap("tab20").colors) + ["#4d4d4d"]

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_france_outline() -> list[list[tuple[float, float]]]:
    with open(DATA_DIR / "france_outline.json", encoding="utf-8") as f:
        outline = json.load(f)
    return [outline["mainland"], outline["corsica"]]


def _draw_france(ax) -> None:
    for polygon in _load_france_outline():
        lons = [point[0] for point in polygon]
        lats = [point[1] for point in polygon]
        ax.fill(lons, lats, color="#eef3ee", zorder=0)
        ax.plot(lons, lats, color="darkgreen", linewidth=1, alpha=0.4, zorder=1)


def plot_villages(villages: pd.DataFrame, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    _draw_france(ax)
    ax.scatter(villages["longitude"], villages["latitude"], s=25, color="darkgreen", zorder=3)
    ax.set_aspect(MAP_ASPECT_RATIO)
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_stages(villages: pd.DataFrame, labels, title: str, out_path: Path, numbered: bool = False) -> None:
    labels = pd.Series(list(labels), index=villages.index)

    fig, ax = plt.subplots(figsize=(8, 8))
    _draw_france(ax)
    for rank, stage in enumerate(sorted(labels.unique())):
        mask = labels == stage
        color = STAGE_COLORS[rank % len(STAGE_COLORS)]
        ax.scatter(villages.loc[mask, "longitude"], villages.loc[mask, "latitude"], s=30, color=color, zorder=3)
        if numbered:
            ax.annotate(
                str(stage),
                (villages.loc[mask, "longitude"].mean(), villages.loc[mask, "latitude"].mean()),
                fontsize=9, fontweight="bold", ha="center", va="center", zorder=5,
                bbox=dict(boxstyle="circle,pad=0.25", facecolor="white", edgecolor=color, linewidth=1.5),
            )
    ax.set_aspect(MAP_ASPECT_RATIO)
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_final_tour(villages: pd.DataFrame, stage_paths: dict, stage_distances: dict, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    _draw_france(ax)
    for stage in sorted(stage_paths):
        path = stage_paths[stage]
        color = STAGE_COLORS[(stage - 1) % len(STAGE_COLORS)]
        lons = [villages["longitude"].iloc[i] for i in path]
        lats = [villages["latitude"].iloc[i] for i in path]
        ax.plot(lons, lats, color=color, linewidth=2, zorder=2)
        ax.scatter(lons, lats, s=20, color=color, zorder=3)
        ax.annotate(
            str(stage), (sum(lons) / len(lons), sum(lats) / len(lats)),
            fontsize=9, fontweight="bold", ha="center", va="center", zorder=5,
            bbox=dict(boxstyle="circle,pad=0.25", facecolor="white", edgecolor=color, linewidth=1.5),
        )
    total = sum(stage_distances.values())
    ax.set_aspect(MAP_ASPECT_RATIO)
    ax.set_title(f"Tour de France 2027 : 21 étapes, {total:.0f} km au total")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_stage_sizes(sizes_kmeans: pd.Series, sizes_cah: pd.Series, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.5), sharey=True)
    sizes_kmeans.sort_values(ascending=False).reset_index(drop=True).plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("Tailles des 21 étapes (K-Means)")
    axes[0].set_ylabel("Nombre de villages")
    sizes_cah.sort_values(ascending=False).reset_index(drop=True).plot(kind="bar", ax=axes[1], color="indianred")
    axes[1].set_title("Tailles des 21 étapes (CAH)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
