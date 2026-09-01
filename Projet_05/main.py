"""Point d'entrée : télécharge le dataset, fine-tune le détecteur, l'évalue.

Usage :
    python main.py

Nécessite un accès réseau (téléchargement du dataset Kaggle ~350 Mo et des
poids pré-entraînés torchvision) et quelques minutes de calcul CPU.
"""

from __future__ import annotations

import random
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision.transforms import v2 as T

from src.data.catalog import build_fish_dataframe, list_images
from src.data.dataset import FishDetectionDataset, collate_fn
from src.data.download import download_dataset
from src.data.yolo import SPECIES
from src.models.detector import build_model
from src.training.train import train
from src.visualization.plots import plot_loss_curves, plot_species_counts

SEED = 42
MAX_TRAIN_IMAGES = 1000
MAX_VAL_IMAGES = 300
BATCH_SIZE = 4
NUM_EPOCHS = 3

PROJECT_ROOT = Path(__file__).resolve().parent
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"


def main() -> None:
    random.seed(SEED)
    torch.manual_seed(SEED)

    dataset_dir = download_dataset(output_dir=str(PROJECT_ROOT / "data"))
    print("Dataset téléchargé dans :", dataset_dir)

    fish_df = build_fish_dataframe(dataset_dir)
    print(f"{len(SPECIES)} espèces, {len(fish_df)} photos étiquetées au total")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_species_counts(fish_df, split="train", out_path=FIGURES_DIR / "species_counts.png")

    all_train = list_images(dataset_dir, "train")
    all_val = list_images(dataset_dir, "valid")
    train_images = random.sample(all_train, min(MAX_TRAIN_IMAGES, len(all_train)))
    val_images = random.sample(all_val, min(MAX_VAL_IMAGES, len(all_val)))

    basic_transform = T.Compose([T.ToDtype(torch.float32, scale=True)])
    train_loader = DataLoader(
        FishDetectionDataset(train_images, transforms=basic_transform),
        batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn,
    )
    print(f"Entraînement : {len(train_images)} photos, {len(train_loader)} batchs de {BATCH_SIZE}")
    print(f"Validation   : {len(val_images)} photos")

    model = build_model(len(SPECIES) + 1)
    loss_history = train(model, train_loader, num_epochs=NUM_EPOCHS)
    plot_loss_curves(loss_history, NUM_EPOCHS, FIGURES_DIR / "loss_curves.png")

    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), CHECKPOINTS_DIR / "fish_detector.pt")
    print(f"Modèle fine-tuné sauvegardé dans {CHECKPOINTS_DIR / 'fish_detector.pt'}")


if __name__ == "__main__":
    main()
