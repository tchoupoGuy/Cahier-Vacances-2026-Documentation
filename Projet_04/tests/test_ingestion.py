from src.ingestion.formatter import full_context


def test_five_pdfs_produce_fifteen_pages(pages):
    assert len(pages) == 15


def test_each_page_has_a_markdown_section(pages):
    assert "section" in pages.columns
    assert all(pages["section"].str.startswith("## "))


def test_full_context_contains_all_titles(pages):
    context = full_context(pages)
    assert context.count("## ") == 15
    assert "## Piscine" in context
