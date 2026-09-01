"""Chargement et adaptation de Faster R-CNN (backbone gelé, tête remplacée)."""

from __future__ import annotations

from torchvision.models.detection import (
    FasterRCNN_MobileNet_V3_Large_320_FPN_Weights,
    fasterrcnn_mobilenet_v3_large_320_fpn,
)
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


def load_pretrained(pretrained: bool = True):
    """Charge Faster R-CNN (MobileNetV3) pré-entraîné sur COCO, en mode évaluation.

    `pretrained=False` construit la même architecture avec des poids
    aléatoires : utile pour tester la logique de gel/adaptation sans
    télécharger de poids (pas d'accès réseau requis).
    """
    weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT if pretrained else None
    return fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights)


def coco_categories() -> list[str]:
    return FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT.meta["categories"]


def build_model(num_classes_with_background: int, pretrained: bool = True):
    """Adapte un Faster R-CNN pré-entraîné à un nouveau jeu de classes.

    Stratégie de fine-tuning : on gèle le backbone (il sait déjà "voir" des
    formes et des contours), et on ne remplace que la tête de classification
    des boîtes, seule partie vraiment concernée par les nouvelles espèces.

    Arguments
    ---------
    num_classes_with_background -- nombre d'espèces à détecter, PLUS la classe fond
    """
    model = load_pretrained(pretrained=pretrained)

    for p in model.backbone.parameters():
        p.requires_grad = False

    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes_with_background)

    return model
