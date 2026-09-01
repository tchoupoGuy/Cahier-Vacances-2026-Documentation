"""Pipeline d'entraînement complet : données brutes -> modèle évalué et sauvegardé."""

from __future__ import annotations

from pathlib import Path

from src.data.loader import add_outcome, filter_modern_era, load_results
from src.evaluation.metrics import evaluate, save_confusion_matrix, save_feature_importances
from src.features.engineering import build_training_table, split_features_target
from src.features.form import add_recent_form
from src.models.train import fit_scaler, save_artifacts, train_random_forest, train_test_split_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "results.csv"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def run_training_pipeline(save: bool = True) -> dict:
    """Enchaîne chargement, feature engineering, entraînement et évaluation.

    Returns un dict avec le modèle, le scaler, les données de test et les
    métriques, pour être réutilisé (simulation du tournoi, notebook, tests).
    """
    df = load_results(DATA_PATH)
    df = filter_modern_era(df)
    df = add_outcome(df)
    df = add_recent_form(df, window=10, min_matches=5)
    df = df.dropna(subset=["home_avg_points", "away_avg_points"]).reset_index(drop=True)

    data = build_training_table(df)
    X, y = split_features_target(data)

    X_train, X_test, y_train, y_test = train_test_split_data(X, y)
    scaler, X_train_scaled = fit_scaler(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = train_random_forest(X_train_scaled, y_train)
    metrics = evaluate(model, X_test_scaled, y_test)

    if save:
        save_artifacts(model, scaler, MODELS_DIR)
        save_confusion_matrix(model, X_test_scaled, y_test, FIGURES_DIR)
        save_feature_importances(model, FIGURES_DIR)

    return {
        "df": df,
        "model": model,
        "scaler": scaler,
        "X_test": X_test,
        "y_test": y_test,
        "accuracy": metrics["accuracy"],
        "baseline": metrics["baseline"],
    }
