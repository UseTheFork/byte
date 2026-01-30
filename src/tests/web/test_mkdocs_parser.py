"""Test suite for MkDocsParser."""

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
async def test_mkdocs_parser_extracts_and_cleans_mkdocs_content(application: Application):
    """Test that MkDocsParser extracts content and ContentCleaner processes it correctly."""

    from byte.web import MkDocsParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)
    cleaner = application.make(ContentCleaner)

    # Verify parser can handle this content
    assert parser.can_parse(soup, "https://docs.example.com/") is True

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

    # Verify cleaning config is correct
    assert config["remove_unwanted"] is True
    assert config["filter_links"] is True
    assert config["link_ratio"] == 1.0
    assert config["to_markdown"] is True


@pytest.mark.asyncio
async def test_mkdocs_parser_can_parse_mkdocs_meta_tag(application: Application):
    """Test that MkDocsParser identifies MkDocs meta tags."""

    from byte.web import MkDocsParser

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)

    # Should detect MkDocs generator meta tag
    assert parser.can_parse(soup, "https://example.com/docs/") is True


@pytest.mark.asyncio
async def test_mkdocs_parser_extracts_content_element(application: Application):
    """Test that MkDocsParser extracts the correct content element."""

    from byte.web import MkDocsParser

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)

    element = parser.extract_content_element(soup)

    assert element is not None
    assert element.name in ["article", "div", "main"]


@pytest.mark.asyncio
async def test_mkdocs_parser_removes_navigation_elements(application: Application):
    """Test that ContentCleaner removes navigation from MkDocs content."""

    from byte.web import MkDocsParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Navigation elements should be removed
    assert "<nav" not in cleaned_content.lower()


@pytest.mark.asyncio
async def test_mkdocs_parser_preserves_code_blocks(application: Application):
    """Test that code blocks are preserved in markdown conversion."""

    from byte.web import MkDocsParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Should contain code blocks
    assert "```" in cleaned_content or "`" in cleaned_content
