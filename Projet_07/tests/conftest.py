import shutil
from pathlib import Path

import pytest

from src.data.brochures import load_brochures
from src.data.database import connect

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture()
def conn(tmp_path):
    """Connexion vers une COPIE de la base : les tests de réservation n'écrivent
    jamais dans data/voyages.db."""
    db_copy = tmp_path / "voyages.db"
    shutil.copy(DATA_DIR / "voyages.db", db_copy)
    connection = connect(db_copy)
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def brochures():
    return load_brochures(DATA_DIR / "hotels")
