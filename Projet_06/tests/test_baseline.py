import numpy as np

from src.baseline.naive import baseline_mean, baseline_yesterday


def test_baseline_mean_repeats_training_average():
    train = np.array([10.0, 20.0, 30.0])
    result = baseline_mean(train, n_test=4)
    assert len(result) == 4
    assert all(result == 20.0)


def test_baseline_yesterday_shifts_by_one_day():
    full_series = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    result = baseline_yesterday(full_series, n_test=3)
    # les 3 derniers jours sont [4, 5, 6] ; "hier" pour chacun est [3, 4, 5]
    assert list(result) == [3.0, 4.0, 5.0]
