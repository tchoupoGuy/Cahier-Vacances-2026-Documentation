from pathlib import Path

import pytest

from src.ingestion.formatter import add_markdown_sections
from src.ingestion.pdf_loader import load_pages

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"


@pytest.fixture(scope="session")
def pages():
    return add_markdown_sections(load_pages(DOCS_DIR))
