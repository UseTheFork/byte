from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


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

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the entire soup as the content element.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                The entire BeautifulSoup object

        Usage: `element = parser.extract_content_element(soup)` -> soup
        """
        return soup

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for raw content parser.

        Returns:
                Dictionary with cleaning pipeline settings (no markdown conversion)

        Usage: `config = parser.get_cleaning_config()` -> dict
        """
        return {
            "remove_unwanted": False,
            "filter_links": False,
            "link_ratio": 1.0,
            "normalize": False,
            "to_markdown": False,
        }
