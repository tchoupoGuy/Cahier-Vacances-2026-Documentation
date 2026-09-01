import pytest

from src.data.loader import add_outcome, filter_modern_era, load_results
from src.pipeline import DATA_PATH, run_training_pipeline


@pytest.fixture(scope="session")
def modern_df():
    df = load_results(DATA_PATH)
    df = filter_modern_era(df)
    df = add_outcome(df)
    return df


@pytest.fixture(scope="session")
def trained():
    # save=False : les tests ne doivent pas dépendre du disque ni le polluer
    return run_training_pipeline(save=False)
