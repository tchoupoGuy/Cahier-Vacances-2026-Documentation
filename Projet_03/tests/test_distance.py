from src.routing.distance import haversine, path_distance


def test_haversine_paris_marseille():
    distance = haversine(48.8566, 2.3522, 43.2965, 5.3698)
    assert 640 < distance < 680


def test_haversine_symmetric():
    a = haversine(48.8566, 2.3522, 43.2965, 5.3698)
    b = haversine(43.2965, 5.3698, 48.8566, 2.3522)
    assert abs(a - b) < 1e-9


def test_haversine_zero_for_same_point():
    assert haversine(45.0, 3.0, 45.0, 3.0) == 0


def test_path_distance_two_points():
    distances = [[0, 10], [10, 0]]
    assert path_distance([0, 1], distances) == 10


def test_path_distance_no_return_trip():
    distances = [[0, 1, 5], [1, 0, 1], [5, 1, 0]]
    # 0 -> 1 -> 2 : ne doit PAS revenir à 0
    assert path_distance([0, 1, 2], distances) == 2
