"""Test suite for GitHubParser."""

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
async def test_github_parser_extracts_and_cleans_github_content(application: Application):
    """Test that GitHubParser extracts content and ContentCleaner processes it correctly."""

    from byte.web import GitHubParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)
    cleaner = application.make(ContentCleaner)

    # Verify parser can handle this content
    assert parser.can_parse(soup, "https://github.com/example/repo") is True

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
    assert config["link_ratio"] == 0.5
    assert config["to_markdown"] is True


@pytest.mark.asyncio
async def test_github_parser_can_parse_github_url(application: Application):
    """Test that GitHubParser identifies GitHub URLs."""

    from byte.web import GitHubParser

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)

    # Should detect GitHub URL
    assert parser.can_parse(soup, "https://github.com/example/repo") is True


@pytest.mark.asyncio
async def test_github_parser_extracts_content_element(application: Application):
    """Test that GitHubParser extracts the correct content element."""

    from byte.web import GitHubParser

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)

    element = parser.extract_content_element(soup)

    assert element is not None
    assert element.name in ["article", "div", "main"]


@pytest.mark.asyncio
async def test_github_parser_removes_navigation_elements(application: Application):
    """Test that ContentCleaner removes navigation from GitHub content."""

    from byte.web import GitHubParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Navigation elements should be removed
    assert "<nav" not in cleaned_content.lower()


@pytest.mark.asyncio
async def test_github_parser_preserves_code_blocks(application: Application):
    """Test that code blocks are preserved in markdown conversion."""

    from byte.web import GitHubParser
    from byte.web.service.content_cleaner import ContentCleaner

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)
    cleaner = application.make(ContentCleaner)

    element = parser.extract_content_element(soup)
    config = parser.get_cleaning_config()

    cleaned_content = cleaner.apply_pipeline(element, **config)

    # Should contain code blocks
    assert "```" in cleaned_content or "`" in cleaned_content
