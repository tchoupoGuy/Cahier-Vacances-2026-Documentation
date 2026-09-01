"""Inférence : faire tourner un détecteur sur une image et ne garder que les détections sûres."""

from __future__ import annotations

import torch
import torchvision.transforms.v2.functional as F
from PIL import Image

from src.data.yolo import SPECIES


def predict(model, image_path: str, names: list[str], score_thresh: float = 0.5):
    """Détecte les objets d'une image et filtre les détections peu confiantes.

    Arguments
    ---------
    model -- un modèle de détection torchvision, en mode eval()
    image_path -- chemin vers une image (n'importe quelle résolution)
    names -- noms des catégories, indexés comme les labels renvoyés par le modèle
    score_thresh -- score de confiance minimum pour garder une détection

    Returns
    -------
    (boxes, labels, scores) -- trois listes de même longueur
    """
    image = Image.open(image_path).convert("RGB")
    image_tensor = F.to_dtype(F.to_image(image), torch.float32, scale=True)
    batch = [image_tensor]

    with torch.no_grad():
        output = model(batch)[0]

    keep = output["scores"] > score_thresh
    boxes = output["boxes"][keep].tolist()
    labels = [names[i] for i in output["labels"][keep].tolist()]
    scores = output["scores"][keep].tolist()

    return boxes, labels, scores


def identify_fish(model, image_path: str, score_thresh: float = 0.5):
    """Prédit avec le modèle fine-tuné : la classe 0 est le fond, les espèces suivent.

    label 1 du modèle -> SPECIES[0], label 2 -> SPECIES[1], etc.
    """
    names = ["background"] + SPECIES
    return predict(model, image_path, names, score_thresh=score_thresh)
