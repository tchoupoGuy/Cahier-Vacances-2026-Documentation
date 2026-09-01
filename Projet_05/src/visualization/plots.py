"""Graphiques : boîtes détectées, comptage par espèce, courbes de perte."""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image

from src.data.yolo import label_path_for, read_yolo_boxes


def plot_boxes(image, boxes, labels, scores=None, ax=None, title=None, box_color="lime"):
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image)
    for i, (box, label) in enumerate(zip(boxes, labels)):
        x1, y1, x2, y2 = box
        ax.add_patch(patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2, edgecolor=box_color, facecolor="none"))
        text = label if scores is None else f"{label} {scores[i]:.2f}"
        ax.text(x1, max(y1 - 4, 0), text, color="black", fontsize=8, bbox=dict(facecolor=box_color, edgecolor="none", pad=1))
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=10)


def plot_species_counts(fish_df, split: str, out_path: Path) -> None:
    counts = fish_df[fish_df["split"] == split]["species"].value_counts()
    counts.sort_values().plot(kind="barh", color="teal", figsize=(7, 5))
    plt.title(f"Nombre de photos par espèce ({split})")
    plt.xlabel("Nombre de photos")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_ground_truth_grid(image_paths: list[str], out_path: Path, n_cols: int = 3) -> None:
    from src.data.yolo import SPECIES

    n_rows = (len(image_paths) + n_cols - 1) // n_cols
    _, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows), squeeze=False)
    axes = [ax for row in axes for ax in row]
    for ax in axes[len(image_paths):]:
        ax.axis("off")

    for ax, image_path in zip(axes, image_paths):
        image = Image.open(image_path).convert("RGB")
        boxes, labels = read_yolo_boxes(label_path_for(image_path), image.width, image.height)
        plot_boxes(image, boxes, [SPECIES[i] for i in labels], ax=ax)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_loss_curves(loss_history: dict[str, list[float]], num_epochs: int, out_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    for name, values in loss_history.items():
        plt.plot(range(1, num_epochs + 1), values, marker="o", label=name)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Courbes de loss (entraînement)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
