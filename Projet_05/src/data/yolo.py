"""Lecture du format d'annotation YOLO (fichiers .txt : une ligne par poisson)."""

from __future__ import annotations

import os
from collections import Counter

SPECIES = [
    "AngelFish", "BlueTang", "ButterflyFish", "ClownFish", "GoldFish", "Gourami",
    "MorishIdol", "PlatyFish", "RibbonedSweetlips", "ThreeStripedDamselfish",
    "YellowCichlid", "YellowTang", "ZebraFish",
]


def label_path_for(image_path: str) -> str:
    """Chemin du fichier d'annotation YOLO correspondant à une image."""
    label_path = image_path.replace(f"{os.sep}images{os.sep}", f"{os.sep}labels{os.sep}")
    return os.path.splitext(label_path)[0] + ".txt"


def read_yolo_boxes(label_path: str, width: int, height: int) -> tuple[list[list[float]], list[int]]:
    """Convertit un fichier YOLO en boîtes pixels [x1, y1, x2, y2] + indices d'espèce.

    Une ligne YOLO est "classe x_centre y_centre largeur hauteur", les 4
    derniers nombres étant des fractions de la taille de l'image.
    """
    boxes, labels = [], []
    with open(label_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 5:
                continue
            class_idx, xc, yc, w, h = parts
            xc, yc, w, h = float(xc), float(yc), float(w), float(h)
            boxes.append([
                (xc - w / 2) * width, (yc - h / 2) * height,
                (xc + w / 2) * width, (yc + h / 2) * height,
            ])
            labels.append(int(class_idx))
    return boxes, labels


def dominant_species(label_path: str) -> str | None:
    """Espèce la plus fréquente d'un fichier d'annotation (None si vide)."""
    _, class_indices = read_yolo_boxes(label_path, 1, 1)
    if not class_indices:
        return None
    most_common_id, _ = Counter(class_indices).most_common(1)[0]
    return SPECIES[most_common_id]
