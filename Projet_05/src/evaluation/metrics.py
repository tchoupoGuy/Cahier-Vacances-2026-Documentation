"""Évaluation objective du détecteur : mean Average Precision (mAP)."""

from __future__ import annotations

import torch


def compute_map(model, data_loader) -> dict:
    """mAP d'un détecteur sur un DataLoader (compare boîtes prédites et vraies boîtes)."""
    from torchmetrics.detection import MeanAveragePrecision

    metric = MeanAveragePrecision(box_format="xyxy")
    model.eval()
    with torch.no_grad():
        for images, targets in data_loader:
            predictions = model(list(images))
            metric.update(list(predictions), list(targets))
    return metric.compute()
