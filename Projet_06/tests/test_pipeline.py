import pytest

from src.pipeline import run_pipeline


@pytest.fixture(scope="session")
def result():
    return run_pipeline()


def test_arma_beats_ma_on_aic(result):
    assert result["arma_result"].aic < result["ma_result"].aic


def test_arma_beats_naive_baselines(result):
    scores = result["scores"]
    best_naive = min(scores["Toujours la moyenne"], scores["Comme hier"])
    arma_key = [k for k in scores if k.startswith("ARMA")][0]
    assert scores[arma_key] < best_naive


def test_residuals_diagnostics_present(result):
    assert set(result["diagnostics"]) == {"MA(3)", "ARMA(1, 1)"}
    for pvalue in result["diagnostics"].values():
        assert 0 <= pvalue <= 1


def test_scores_table_sorted_best_first(result):
    table = result["scores_table"]
    errors = table["erreur moyenne (glaces/jour)"].tolist()
    assert errors == sorted(errors)
