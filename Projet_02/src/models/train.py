"""Découpage train/test, standardisation et entraînement du modèle."""

from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 200


def train_test_split_data(X: pd.DataFrame, y: pd.Series):
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def fit_scaler(X_train: pd.DataFrame) -> tuple[StandardScaler, "np.ndarray"]:
    """Ajuste le scaler UNIQUEMENT sur le train, puis le transforme."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    return scaler, X_train_scaled


def train_random_forest(X_train_scaled, y_train) -> RandomForestClassifier:
    model = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE)
    model.fit(X_train_scaled, y_train)
    return model


def save_artifacts(model, scaler, models_dir) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "random_forest.joblib")
    joblib.dump(scaler, models_dir / "scaler.joblib")


def load_artifacts(models_dir):
    model = joblib.load(models_dir / "random_forest.joblib")
    scaler = joblib.load(models_dir / "scaler.joblib")
    return model, scaler
