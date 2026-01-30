from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class MkDocsParser(BaseWebParser):
    """Parser for MkDocs documentation sites.

    Extracts main content from MkDocs pages by identifying specific HTML tags
    and filtering out navigation, search, and other non-content elements.
    """

    def boot(self, exclude_links_ratio: float = 1.0, **kwargs):
        """Initialize MkDocs parser.

        Args:
                exclude_links_ratio: The ratio of links:content to exclude pages from.
                        This reduces the frequency at which index pages make their way into results.
                        Recommended: 0.5
        """
        self.exclude_links_ratio = exclude_links_ratio

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is an MkDocs page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this appears to be an MkDocs page

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        # Check for MkDocs-specific meta tags
        mkdocs_meta = soup.find("meta", attrs={"name": "generator", "content": lambda x: x and "mkdocs" in x.lower()})
        if mkdocs_meta:
            return True

        # Check for common MkDocs HTML structure
        if soup.find("div", class_="md-content") or soup.find("article", class_="md-content__inner"):
            return True

        # Check for MkDocs Material theme
        if soup.find("div", {"data-md-component": "container"}):
            return True

        return False

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from MkDocs HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        # Default tags to search for main content
        html_tags = [
            ("article", {"class": "md-content__inner"}),
            ("div", {"class": "md-content"}),
            ("main", {}),
            ("article", {}),
        ]

        # Search for main content element
        for tag, attrs in html_tags:
            element = soup.find(tag, attrs)
            if element is not None:
                return element

        return None

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for MkDocs parser.

        Returns:
                Dictionary with cleaning pipeline settings

        Usage: `config = parser.get_cleaning_config()` -> dict
        """
        return {
            "remove_unwanted": True,
            "filter_links": True,
            "link_ratio": self.exclude_links_ratio,
            "normalize": False,
            "to_markdown": True,
        }
