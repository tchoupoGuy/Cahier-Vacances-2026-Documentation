from src.routing.distance import path_distance
from src.routing.heuristics import greedy_path, two_opt


def _square_distances():
    # 4 points formant un carré, avec un ordre initial volontairement croisé
    #   0 --- 1
    #   |     |
    #   3 --- 2
    return [
        [0, 1, 1.41, 1],
        [1, 0, 1, 1.41],
        [1.41, 1, 0, 1],
        [1, 1.41, 1, 0],
    ]


def test_greedy_path_visits_every_village_once():
    distances = _square_distances()
    path = greedy_path([0, 1, 2, 3], start=0, distances=distances)
    assert path[0] == 0
    assert set(path) == {0, 1, 2, 3}
    assert len(path) == 4


def test_two_opt_never_lengthens_the_path():
    distances = _square_distances()
    # un ordre volontairement mauvais (diagonale, diagonale)
    bad_path = [0, 2, 1, 3]
    improved = two_opt(bad_path, distances)
    assert set(improved) == set(bad_path)
    assert path_distance(improved, distances) <= path_distance(bad_path, distances) + 1e-9
