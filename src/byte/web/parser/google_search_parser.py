from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class GoogleSearchParser(BaseWebParser):
    """Parser for Google Search results pages.

    Extracts search result entries from Google Search HTML, including
    titles, snippets, and URLs, while filtering out ads and navigation.
    """

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a Google Search results page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this is a Google Search results page, False otherwise

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """

        return True

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main search results container from Google Search HTML.

        Tries to find the results in this order:
        1. <div id="search"> — primary search results container
        2. <div id="rcnt"> — results content wrapper
        3. <div id="main"> — main content area
        4. <body> — fallback

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the search results, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        content_selectors = [
            ("div", {"id": "search"}),
            ("div", {"id": "rcnt"}),
            ("div", {"id": "main"}),
            ("body", {}),
        ]

        for tag, attrs in content_selectors:
            element = soup.find(tag, attrs)
            if element is not None:
                return element

        return None

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for Google Search parser.

        Returns:
                Dictionary with cleaning pipeline settings

        Usage: `config = parser.get_cleaning_config()` -> dict
        """
        return {
            "remove_unwanted": True,
            "filter_links": False,
            "link_ratio": 1.0,
            "normalize": False,
            "to_markdown": False,
        }
