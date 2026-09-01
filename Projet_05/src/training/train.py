"""Boucle d'entraînement du détecteur fine-tuné."""

from __future__ import annotations

import torch

LOSS_NAMES = ["loss_classifier", "loss_box_reg", "loss_objectness", "loss_rpn_box_reg"]


def build_optimizer(model, lr: float = 0.005, momentum: float = 0.9, weight_decay: float = 5e-4):
    """Optimiseur SGD sur les seuls paramètres entraînables (le backbone est gelé)."""
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    return torch.optim.SGD(trainable_params, lr=lr, momentum=momentum, weight_decay=weight_decay)


def train_one_epoch(model, data_loader, optimizer) -> dict[str, float]:
    """Une époque d'entraînement, renvoie la moyenne de chacune des 4 pertes.

    En mode `.train()`, `model(images, targets)` ne renvoie PAS des
    prédictions mais un dictionnaire de 4 pertes (une par sous-partie du
    réseau) : on les additionne pour obtenir la perte totale à rétropropager.
    """
    model.train()
    running = {name: 0.0 for name in LOSS_NAMES}
    n_batches = 0

    for images, targets in data_loader:
        images, targets = list(images), list(targets)

        loss_dict = model(images, targets)
        loss = sum(loss_dict.values())

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        for name in LOSS_NAMES:
            running[name] += loss_dict[name].item()
        n_batches += 1

    return {name: running[name] / n_batches for name in LOSS_NAMES}


def train(model, data_loader, num_epochs: int, optimizer=None) -> dict[str, list[float]]:
    """Enchaîne `num_epochs` époques et renvoie l'historique de chaque perte."""
    optimizer = optimizer or build_optimizer(model)
    loss_history = {name: [] for name in LOSS_NAMES}

    for epoch in range(num_epochs):
        epoch_losses = train_one_epoch(model, data_loader, optimizer)
        for name in LOSS_NAMES:
            loss_history[name].append(epoch_losses[name])
        total = sum(epoch_losses.values())
        print(f"epoch {epoch + 1}/{num_epochs}  loss totale {total:.3f}")

    return loss_history
