from src.rag_pipeline import answer_naive, answer_with_rag
from src.retrieval.vector_store import VectorStore
from tests.fakes import FakeEmbedder, FakeGenerator
from tests.test_vector_store import SYNTHETIC_PAGES, VOCABULARY


def test_answer_naive_includes_full_context_in_prompt(pages):
    from src.ingestion.formatter import full_context

    generator = FakeGenerator()
    context = full_context(pages)
    answer = answer_naive(generator, context, "Le wifi est-il gratuit ?")
    assert "réponse factice" in answer


def test_answer_with_rag_returns_matching_source():
    store = VectorStore(SYNTHETIC_PAGES, FakeEmbedder(VOCABULARY))
    generator = FakeGenerator()

    answer, sources = answer_with_rag(generator, store, "Est-ce qu'il y a une piscine ?", top_k=1)

    assert "réponse factice" in answer
    assert sources.iloc[0]["title"] == "Piscine"
