from pathlib import Path

from src.data.loader import load_sales, train_test_split_series

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "ventes_glaces.csv"


def test_load_sales_parses_dates():
    df = load_sales(DATA_PATH)
    assert len(df) == 488
    assert list(df.columns) == ["date", "saison", "ventes"]
    assert df["date"].dtype.kind == "M"  # datetime


def test_train_test_split_is_chronological():
    df = load_sales(DATA_PATH)
    ventes = df["ventes"].to_numpy(dtype=float)
    train, test, dates_test = train_test_split_series(ventes, df["date"], n_test=22)

    assert len(train) == 488 - 22
    assert len(test) == 22
    assert len(dates_test) == 22
    assert list(test) == list(ventes[-22:])
