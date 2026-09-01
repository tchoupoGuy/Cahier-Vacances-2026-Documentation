"""Livre de route : mise en forme texte du Tour final."""

from __future__ import annotations

import pandas as pd


def print_roadbook(villages: pd.DataFrame, stage_paths: dict, stage_distances: dict) -> None:
    total = sum(stage_distances.values())
    longest = max(stage_distances, key=stage_distances.get)
    shortest = min(stage_distances, key=stage_distances.get)

    print("=" * 78)
    print("Livre de route officiel - Tour de France 2027".center(78))
    print("=" * 78)
    for stage in sorted(stage_paths):
        path = stage_paths[stage]
        start = villages["village"].iloc[path[0]]
        finish = villages["village"].iloc[path[-1]]
        badge = ""
        if stage == longest:
            badge = "  (etape reine)"
        elif stage == shortest:
            badge = "  (la plus courte)"
        line = f"Etape {stage:>2} | {start} -> {finish}"
        print(f"{line:<58} | {len(path):>2} villages | {stage_distances[stage]:>4.0f} km{badge}")
    print("-" * 78)
    print(f"{'TOTAL':<58} | {sum(len(p) for p in stage_paths.values()):>2} villages | {total:>4.0f} km")
    print("=" * 78)
