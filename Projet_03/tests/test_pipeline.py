import pytest

from src.pipeline import run_pipeline


@pytest.fixture(scope="session")
def result():
    return run_pipeline()


def test_villages_loaded(result):
    assert len(result["villages"]) == 120


def test_21_stages_covering_all_villages(result):
    villages = result["villages"]
    assert set(villages["stage"]) == set(range(1, 22))


def test_silhouette_scores_in_expected_range(result):
    comparison = result["comparison"]
    assert 0.30 < comparison["silhouette_kmeans"] < 0.60
    assert 0.30 < comparison["silhouette_cah"] < 0.60


def test_every_village_routed_exactly_once(result):
    all_visited = [village for path in result["stage_paths"].values() for village in path]
    assert len(all_visited) == 120
    assert set(all_visited) == set(range(120))


def test_total_distance_in_expected_range(result):
    assert 3600 < result["total_distance"] < 4600
