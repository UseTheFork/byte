"""Test suite for web content parsers."""

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
async def test_sphinx_parser_can_parse_readthedocs_fixture(application: Application):
    """Test that SphinxParser correctly identifies ReadTheDocs pages using fixture."""

    from byte.web import SphinxParser

    fixture_path = Path(__file__).parent / "fixtures" / "readthedocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(SphinxParser)

    assert (
        parser.can_parse(soup, "https://python-semantic-release.readthedocs.io/en/latest/concepts/commit_parsing.html")
        is True
    )


@pytest.mark.asyncio
async def test_mkdocs_parser_can_parse_mkdocs_fixture(application: Application):
    """Test that MkDocsParser correctly identifies MkDocs pages using fixture."""

    from byte.web import MkDocsParser

    fixture_path = Path(__file__).parent / "fixtures" / "mkdocs-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(MkDocsParser)

    assert parser.can_parse(soup, "https://docs.example.com/") is True


@pytest.mark.asyncio
async def test_github_parser_can_parse_github_fixture(application: Application):
    """Test that GitHubParser correctly identifies GitHub pages using fixture."""

    from byte.web import GitHubParser

    fixture_path = Path(__file__).parent / "fixtures" / "github-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitHubParser)

    assert parser.can_parse(soup, "https://github.com/example/repo") is True


@pytest.mark.asyncio
async def test_gitbook_parser_can_parse_gitbook_fixture(application: Application):
    """Test that GitBookParser correctly identifies GitBook pages using fixture."""

    from byte.web import GitBookParser

    fixture_path = Path(__file__).parent / "fixtures" / "gitbook-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GitBookParser)

    assert parser.can_parse(soup, "https://docs.gitbook.com/") is True


@pytest.mark.asyncio
async def test_generic_parser_can_parse_mintlify_fixture(application: Application):
    """Test that GenericParser can handle Mintlify pages using fixture."""

    from byte.web import GenericParser

    fixture_path = Path(__file__).parent / "fixtures" / "mintlify-1.txt"
    html = fixture_path.read_text()

    soup = BeautifulSoup(html, "html.parser")
    parser = application.make(GenericParser)

    assert parser.can_parse(soup, "https://docs.example.com/") is True
