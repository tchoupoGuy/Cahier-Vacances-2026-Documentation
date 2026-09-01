"""Construction du catalogue des photos (une ligne par photo étiquetée)."""

from __future__ import annotations

import os

import pandas as pd

from src.data.yolo import dominant_species, label_path_for


def list_images(dataset_dir: str, split: str) -> list[str]:
    """Liste les chemins d'images d'un split ("train", "valid" ou "test")."""
    image_dir = os.path.join(dataset_dir, split, "images")
    return sorted(os.path.join(image_dir, name) for name in os.listdir(image_dir))


def build_fish_dataframe(dataset_dir: str) -> pd.DataFrame:
    """DataFrame avec une ligne par photo étiquetée : image_path, species (dominante), split."""
    rows = []
    for split in ("train", "valid", "test"):
        for image_path in list_images(dataset_dir, split):
            label_path = label_path_for(image_path)
            if not os.path.exists(label_path):
                continue
            species = dominant_species(label_path)
            if species is not None:
                rows.append({"image_path": image_path, "species": species, "split": split})
    return pd.DataFrame(rows)
