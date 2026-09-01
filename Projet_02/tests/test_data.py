def test_modern_era_filter(modern_df):
    assert modern_df["year"].min() == 1994
    assert str(modern_df["date"].max()) <= "2026-06-30 00:00:00"
    assert 28000 < len(modern_df) < 32000


def test_home_advantage(modern_df):
    non_neutral = modern_df[modern_df["neutral"] == False]  # noqa: E712
    proportions = non_neutral["outcome"].value_counts(normalize=True)
    assert abs(proportions.sum() - 1.0) < 0.01
    assert proportions["home_win"] > proportions["away_win"]
    assert 0.45 < proportions["home_win"] < 0.55


def test_top_10_teams_contains_brazil(modern_df):
    home_wins = modern_df[modern_df["outcome"] == "home_win"]["home_team"].value_counts()
    away_wins = modern_df[modern_df["outcome"] == "away_win"]["away_team"].value_counts()
    total_wins = home_wins.add(away_wins, fill_value=0).sort_values(ascending=False)
    top_10 = total_wins.head(10)

    assert len(top_10) == 10
    assert "Brazil" in top_10.index
    assert top_10.is_monotonic_decreasing


def test_goals_per_year_is_stable(modern_df):
    goals_per_year = (
        (modern_df["home_score"] + modern_df["away_score"]).groupby(modern_df["year"]).mean()
    )
    assert len(goals_per_year) > 30
    assert goals_per_year.between(2, 4).all()
