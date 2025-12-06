from bs4 import BeautifulSoup

from byte.domain.web.parser.base import BaseWebParser


class RawContentParser(BaseWebParser):
    """Fallback parser that returns content as-is without any processing.

    This parser always returns True for can_parse and simply extracts
    all text content from the page without any filtering or markdown conversion.
    Used as the absolute last resort when no other parser matches.
    """

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Always returns True as this is the ultimate fallback parser.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                Always True to serve as final fallback

        Usage: `if parser.can_parse(soup, url)` -> True
        """
        return True

    def parse(self, soup: BeautifulSoup) -> str:
        """Extract raw text content without any processing.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Raw text content as a string

        Usage: `text = parser.parse(soup)` -> raw text
        """
        return self._get_clean_text(soup)
