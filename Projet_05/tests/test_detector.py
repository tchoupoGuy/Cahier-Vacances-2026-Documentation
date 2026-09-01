"""Teste la logique de gel/adaptation du modèle, sans télécharger de poids pré-entraînés.

Ce test est automatiquement ignoré si `torch`/`torchvision` ne sont pas
installés (voir README : ce projet nécessite un environnement plus lourd
que les autres, comme le note le notebook d'origine qui recommande Colab).
"""

import pytest

torch = pytest.importorskip("torch")


def test_build_model_freezes_backbone_and_adapts_head():
    from src.models.detector import build_model

    # pretrained=False : pas de téléchargement de poids, juste l'architecture
    model = build_model(num_classes_with_background=14, pretrained=False)

    assert all(not p.requires_grad for p in model.backbone.parameters())
    assert model.roi_heads.box_predictor.cls_score.out_features == 14
