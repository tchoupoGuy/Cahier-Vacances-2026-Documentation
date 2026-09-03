import pandas as pd

from src.ingestion.chunking import chunk_pages, split_into_chunks


class TestSplitIntoChunks:
    def test_short_text_returns_a_single_chunk(self):
        assert split_into_chunks("Le wifi est gratuit dans tout l'hôtel.", size=500) == [
            "Le wifi est gratuit dans tout l'hôtel."
        ]

    def test_long_text_is_split_into_multiple_chunks(self):
        text = "Phrase numéro un. " * 100  # largement plus que 500 caractères
        chunks = split_into_chunks(text, size=500, overlap=80)

        assert len(chunks) > 1
        assert all(len(c) <= 500 + 1 for c in chunks)  # marge de 1 pour l'espace de coupure

    def test_prefers_cutting_at_sentence_boundary(self):
        # La coupure doit tomber juste après le point, pas au milieu d'un mot suivant.
        # Note : la recherche de fin de phrase ne porte que sur la seconde moitié de la
        # fenêtre (`start + size // 2` à `end`, voir split_into_chunks) — un point trop
        # proche du DÉBUT du chunk n'est donc pas retenu, seulement un point situé après
        # la moitié de la taille cible.
        text = "Une phrase pas trop courte ici. " + "mot " * 200
        chunks = split_into_chunks(text, size=50, overlap=10)

        assert chunks[0] == "Une phrase pas trop courte ici."

    def test_overlap_repeats_the_tail_of_the_previous_chunk(self):
        text = "Phrase numéro un. " * 50
        chunks = split_into_chunks(text, size=200, overlap=50)

        # La fin du premier chunk doit se retrouver au début du second (chevauchement).
        assert chunks[1].startswith(chunks[0][-30:]) or chunks[0][-30:] in chunks[1][:80]

    def test_empty_text_returns_no_chunks(self):
        assert split_into_chunks("   ", size=500) == []

    def test_invalid_size_raises(self):
        import pytest

        with pytest.raises(ValueError):
            split_into_chunks("un texte", size=0)

    def test_overlap_not_smaller_than_size_raises(self):
        import pytest

        with pytest.raises(ValueError):
            split_into_chunks("un texte", size=100, overlap=100)


class TestChunkPages:
    def test_output_has_same_columns_as_load_pages(self):
        pages = pd.DataFrame([{"source": "a.pdf", "title": "Wifi", "text": "Le wifi est gratuit."}])

        chunked = chunk_pages(pages, size=500)

        assert list(chunked.columns) == ["source", "title", "text"]

    def test_long_page_becomes_several_traceable_chunks(self):
        long_text = "Le sauna est ouvert de 8h à 20h. " * 30
        pages = pd.DataFrame([{"source": "spa.pdf", "title": "Spa", "text": long_text}])

        chunked = chunk_pages(pages, size=200, overlap=40)

        assert len(chunked) > 1
        assert (chunked["source"] == "spa.pdf").all()
        assert chunked["title"].tolist() == [f"Spa · passage {i}" for i in range(1, len(chunked) + 1)]

    def test_short_page_stays_a_single_chunk(self):
        pages = pd.DataFrame([{"source": "a.pdf", "title": "Wifi", "text": "Le wifi est gratuit."}])

        chunked = chunk_pages(pages, size=500)

        assert len(chunked) == 1
        assert chunked.iloc[0]["title"] == "Wifi · passage 1"

    def test_multiple_pages_are_each_chunked_independently(self):
        pages = pd.DataFrame([
            {"source": "a.pdf", "title": "Wifi", "text": "Le wifi est gratuit."},
            {"source": "b.pdf", "title": "Sauna", "text": "Le sauna est ouvert de 8h à 20h. " * 30},
        ])

        chunked = chunk_pages(pages, size=200, overlap=40)

        assert (chunked[chunked["source"] == "a.pdf"]).shape[0] == 1
        assert (chunked[chunked["source"] == "b.pdf"]).shape[0] > 1

    def test_compatible_with_add_markdown_sections(self):
        # Le vrai test d'intégration : ce que produit chunk_pages doit pouvoir
        # traverser add_markdown_sections puis VectorStore sans modification.
        from src.ingestion.formatter import add_markdown_sections

        pages = pd.DataFrame([{"source": "a.pdf", "title": "Wifi", "text": "Le wifi est gratuit."}])
        chunked = chunk_pages(pages, size=500)

        sectioned = add_markdown_sections(chunked)

        assert "section" in sectioned.columns
        assert sectioned.iloc[0]["section"] == "## Wifi · passage 1\n\nLe wifi est gratuit."
