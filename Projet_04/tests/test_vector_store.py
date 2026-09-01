import pandas as pd

from src.retrieval.vector_store import VectorStore
from tests.fakes import FakeEmbedder

# Un petit corpus synthétique et sans ambiguïté, pour tester la MÉCANIQUE de
# recherche indépendamment du contenu réel (fragile et sujet à des
# chevauchements de mots-clés entre rubriques de l'hôtel).
SYNTHETIC_PAGES = pd.DataFrame([
    {"title": "Piscine", "section": "La piscine est ouverte de 8h à 20h."},
    {"title": "Wifi", "section": "Le wifi est gratuit dans tout l'hôtel."},
    {"title": "Animaux", "section": "Les chiens sont acceptés sur demande."},
])
VOCABULARY = ["piscine", "wifi", "chien"]


def test_search_retrieves_the_matching_page():
    store = VectorStore(SYNTHETIC_PAGES, FakeEmbedder(VOCABULARY))

    results = store.search("Est-ce qu'il y a une piscine ?", top_k=1)

    assert results.iloc[0]["title"] == "Piscine"


def test_search_orders_results_by_decreasing_score():
    store = VectorStore(SYNTHETIC_PAGES, FakeEmbedder(VOCABULARY))
    results = store.search("wifi et chiens", top_k=3)
    assert "score" in results.columns
    assert results["score"].is_monotonic_decreasing


def test_search_top_k_is_respected():
    store = VectorStore(SYNTHETIC_PAGES, FakeEmbedder(VOCABULARY))
    results = store.search("wifi", top_k=2)
    assert len(results) == 2
