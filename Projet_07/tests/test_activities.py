from src.data.database import query
from src.tools.activities import find_activities


def test_find_activities_returns_expected_columns(conn):
    activites = find_activities(conn, "Rome")
    assert list(activites.columns) == ["nom", "categorie", "duree_h", "prix_eur"]


def test_find_activities_matches_total_count(conn):
    activites = find_activities(conn, "Rome")
    attendu = query(conn, "SELECT COUNT(*) AS n FROM activites WHERE ville = ?", ("Rome",)).iloc[0]["n"]
    assert len(activites) == attendu


def test_find_activities_sorted_by_price(conn):
    activites = find_activities(conn, "Rome")
    assert activites["prix_eur"].is_monotonic_increasing
