def test_accuracy_beats_baseline(trained):
    assert trained["accuracy"] > 0.60
    assert trained["accuracy"] > trained["baseline"] - 0.05  # au moins aussi bon qu'un réflexe naïf


def test_train_test_split_sizes(trained):
    assert len(trained["X_test"]) > 0
    assert len(trained["X_test"]) == len(trained["y_test"])


def test_feature_importances_sum_to_one(trained):
    importances = trained["model"].feature_importances_
    assert abs(importances.sum() - 1.0) < 1e-6
