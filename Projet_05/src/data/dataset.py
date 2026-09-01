"""Dataset PyTorch : sert une image et ses boîtes annotées au format attendu par Faster R-CNN."""

from __future__ import annotations

import torch
from torch.utils.data import Dataset
from torchvision import tv_tensors
from torchvision.io import read_image

from src.data.yolo import label_path_for, read_yolo_boxes


class FishDetectionDataset(Dataset):
    """Un échantillon = une image + ses boîtes (poissons) au format torchvision.

    torchvision réserve la classe 0 au "fond" (l'absence d'objet) : les
    espèces (indices 0 à 12 dans SPECIES) sont donc décalées de +1 (labels
    1 à 13) pour le modèle.
    """

    def __init__(self, image_paths: list[str], transforms=None):
        self.image_paths = image_paths
        self.transforms = transforms

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, i: int):
        image_path = self.image_paths[i]
        image = read_image(image_path)[:3]  # ignore un éventuel canal alpha
        h, w = image.shape[-2:]
        boxes, class_indices = read_yolo_boxes(label_path_for(image_path), w, h)

        boxes_t = torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4)
        # dtype=torch.int64 obligatoire : sur une photo sans poisson, la liste est vide
        # et torch.tensor([]) fabriquerait des float, que le modèle refuse.
        labels_t = torch.tensor([c + 1 for c in class_indices], dtype=torch.int64)

        target = {
            "boxes": tv_tensors.BoundingBoxes(boxes_t, format="XYXY", canvas_size=(h, w)),
            "labels": labels_t,
        }
        image = tv_tensors.Image(image)

        if self.transforms:
            image, target = self.transforms(image, target)

        return image, target


def collate_fn(batch):
    """Regroupe une liste de (image, target) en deux tuples.

    Les images et le nombre de boîtes variant d'un échantillon à l'autre, on
    ne peut pas les empiler (`torch.stack`) : on les garde en listes.
    """
    return tuple(zip(*batch))
