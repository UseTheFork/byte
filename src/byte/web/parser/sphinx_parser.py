from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class SphinxParser(BaseWebParser):
    """Parser for Sphinx documentation sites.

    Extracts main content from Sphinx-generated documentation by identifying
    specific HTML structure and filtering out navigation and sidebar elements.
    """

    def boot(self, exclude_links_ratio: float = 1.0, **kwargs):
        """Initialize Sphinx parser.

        Args:
                exclude_links_ratio: The ratio of links:content to exclude pages from.
                        This reduces the frequency at which index pages make their way into results.
                        Recommended: 0.5
        """
        self.exclude_links_ratio = exclude_links_ratio

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a Sphinx-generated page or ReadTheDocs site.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this appears to be a Sphinx or ReadTheDocs page

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        # Check for ReadTheDocs URL
        if "readthedocs" in url.lower():
            return True

        # Check for Sphinx-specific meta tags
        sphinx_meta = soup.find("meta", attrs={"name": "generator", "content": lambda x: x and "sphinx" in x.lower()})
        if sphinx_meta:
            return True

        # Check for common Sphinx HTML structure
        if soup.find("div", class_="document") or soup.find("div", class_="documentwrapper"):
            return True

        # Check for Sphinx-specific classes
        if soup.find("div", class_="body") and soup.find("div", class_="sphinxsidebar"):
            return True

        # Check for ReadTheDocs-specific structure
        if soup.find("div", {"role": "main"}) or soup.find("main", {"id": "main-content"}):
            return True

        return False

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from Sphinx or ReadTheDocs HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        # Default tags to search for main content (Sphinx and ReadTheDocs)
        html_tags = [
            ("div", {"role": "main"}),
            ("main", {"id": "main-content"}),
            ("div", {"class": "body"}),
            ("div", {"class": "document"}),
            ("div", {"class": "documentwrapper"}),
            ("main", {}),
        ]

        # Search for main content element
        for tag, attrs in html_tags:
            element = soup.find(tag, attrs)
            if element is not None:
                return element

        return None

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for Sphinx parser.

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
