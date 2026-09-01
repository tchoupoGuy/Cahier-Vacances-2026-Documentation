from src.models.predict import predict_match


def test_predict_match_is_symmetric(trained):
    model, scaler, df = trained["model"], trained["scaler"], trained["df"]

    winner_1, proba_1 = predict_match(model, scaler, df, "France", "Greece")
    winner_2, proba_2 = predict_match(model, scaler, df, "Greece", "France")

    assert winner_1 == "France"
    assert winner_2 == "France"
    assert 0.5 <= proba_1 <= 1
    assert 0.5 <= proba_2 <= 1
