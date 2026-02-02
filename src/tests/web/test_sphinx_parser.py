"""Test suite for SphinxParser."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide WebServiceProvider for parser tests."""
    from byte.web import WebServiceProvider

    return [WebServiceProvider]


@pytest.mark.asyncio
async def test_sphinx_parser_extracts_and_cleans_readthedocs_content(application: Application):
    """Test that SphinxParser extracts content and ContentCleaner processes it correctly."""

    from byte.web import SphinxParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)
    cleaner = application.make(ContentCleaner)

    # Verify parser can handle this content
    assert parser.can_parse(soup, "https://python-semantic-release.readthedocs.io/en/latest/") is True

    # Extract content element
    element = parser.extract_content_element(soup)
    assert element is not None

    # Get cleaning config from parser
    config = parser.get_cleaning_config()

    # Apply cleaning pipeline
    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Basic assertions
    assert len(cleaned_content) > 0
    assert isinstance(cleaned_content, str)

    # Verify it extracted the article element
    assert element.name == "article"

    # Verify it has substantial content
    assert len(element.find_all()) > 600

    # Verify cleaning config is correct
    assert config["remove_unwanted"] is True
    assert config["filter_links"] is True
    assert config["link_ratio"] == 1.0
    assert config["to_markdown"] is True

    # Verify cleaned content is substantial and in markdown format
    assert len(cleaned_content) > 15000
    assert cleaned_content.startswith("# Python Semantic Release")
    assert "¶" in cleaned_content  # Sphinx permalink markers
    assert "[![" in cleaned_content  # Markdown image links (badges)


@pytest.mark.asyncio
async def test_sphinx_parser_can_parse_readthedocs_url(application: Application):
    """Test that SphinxParser identifies ReadTheDocs URLs."""

    from byte.web import SphinxParser

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)

    # Should detect ReadTheDocs URL
    assert parser.can_parse(soup, "https://python-semantic-release.readthedocs.io/en/latest/") is True


@pytest.mark.asyncio
async def test_sphinx_parser_extracts_article_element(application: Application):
    """Test that SphinxParser extracts the correct article element."""

    from byte.web import SphinxParser

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)

    element = parser.extract_content_element(soup)

    assert element is not None
    assert element.name == "article"
    assert element.get("role") == "main"


@pytest.mark.asyncio
async def test_sphinx_parser_removes_navigation_elements(application: Application):
    """Test that ContentCleaner removes navigation from Sphinx content."""

    from byte.web import SphinxParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Navigation elements should be removed
    assert "<nav" not in cleaned_content.lower()
    assert "aria-label" not in cleaned_content.lower()


@pytest.mark.asyncio
async def test_sphinx_parser_preserves_code_blocks(application: Application):
    """Test that code blocks are preserved in markdown conversion."""

    from byte.web import SphinxParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Should contain code blocks
    assert "```" in cleaned_content or "`" in cleaned_content
