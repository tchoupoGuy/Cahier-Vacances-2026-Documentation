"""Évaluation du modèle : accuracy, matrice de confusion, importance des features."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score

from src.features.engineering import FEATURES


def evaluate(model, X_test_scaled, y_test) -> dict:
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    baseline = y_test.mean()  # toujours prédire "victoire à domicile"
    return {"accuracy": accuracy, "baseline": baseline, "y_pred": y_pred}


def save_confusion_matrix(model, X_test_scaled, y_test, figures_dir: Path) -> Path:
    figures_dir.mkdir(parents=True, exist_ok=True)
    ConfusionMatrixDisplay.from_estimator(
        model, X_test_scaled, y_test,
        display_labels=["Pas de victoire domicile", "Victoire domicile"],
        cmap="Blues", colorbar=False,
    )
    plt.title("Matrice de confusion sur le jeu de test")
    plt.tight_layout()
    out_path = figures_dir / "confusion_matrix.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def save_feature_importances(model, figures_dir: Path) -> Path:
    figures_dir.mkdir(parents=True, exist_ok=True)
    importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values()

    importances.plot(kind="barh", color="seagreen")
    plt.title("Importance de chaque feature dans les prédictions")
    plt.xlabel("Importance")
    plt.tight_layout()
    out_path = figures_dir / "feature_importances.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path
