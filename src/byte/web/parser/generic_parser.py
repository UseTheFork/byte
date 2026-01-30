from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class GenericParser(BaseWebParser):
    """Generic fallback parser for any HTML content.

    This parser attempts to extract the main content from common HTML structures
    like <main>, <article>, or <body> tags. It always returns True for can_parse
    so it can be used as a last resort fallback.
    """

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Check if parser can extract content from the page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if parse() returns non-empty content, False otherwise

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        content = self.parse(soup)
        return bool(content.strip())

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from common HTML containers.

        Tries to find content in this order:
        1. <main> tag
        2. <article> tag
        3. <div role="main">
        4. <body> tag

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        # Try common content containers in order of preference
        content_selectors = [
            ("main", {}),
            ("article", {}),
            ("div", {"role": "main"}),
            ("body", {}),
        ]

        for tag, attrs in content_selectors:
            element = soup.find(tag, attrs)
            if element is not None:
                return element

        return None

    def parse(self, soup: BeautifulSoup) -> str:
        """Extract text from common HTML content containers.

        Tries to find content in this order:
        1. <main> tag
        2. <article> tag
        3. <div role="main">
        4. <body> tag

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Cleaned text content as a string

        Usage: `text = parser.parse(soup)` -> cleaned text
        """
        # Try common content containers in order of preference
        content_selectors = [
            ("main", {}),
            ("article", {}),
            ("div", {"role": "main"}),
            ("body", {}),
        ]

        element = None
        for tag, attrs in content_selectors:
            element = soup.find(tag, attrs)
            if element is not None:
                break

        # If we found an element, return its markdown content
        if element is not None:
            return self._to_markdown(element)
        else:
            return ""
