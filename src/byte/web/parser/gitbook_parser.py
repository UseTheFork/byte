from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class GitBookParser(BaseWebParser):
    """Parser for GitBook documentation sites.

    Extracts main content from GitBook pages by identifying specific HTML structure
    and filtering out navigation, sidebars, and other non-content elements.
    """

    def boot(self, exclude_links_ratio: float = 1.0, **kwargs) -> None:
        """Initialize GitBook parser.

        Args:
                exclude_links_ratio: Maximum ratio of link text to total text (0.0 to 1.0).
                        Pages exceeding this ratio will return empty content.
        """
        self.exclude_links_ratio = exclude_links_ratio

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a GitBook page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this appears to be a GitBook page

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        # Check for GitBook URL patterns
        if "gitbook.io" in url.lower() or "gitbook.com" in url.lower():
            return True

        # Check for GitBook-specific meta tags
        gitbook_meta = soup.find("meta", attrs={"name": "generator", "content": lambda x: x and "gitbook" in x.lower()})  # pyright: ignore[reportCallIssue]
        if gitbook_meta:
            return True

        # Check for GitBook-specific classes or data attributes
        if soup.find("div", class_=lambda x: x and "gitbook" in x.lower()):
            return True

        if soup.find("div", attrs={"data-gitbook": True}):
            return True

        return False

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from GitBook HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        # GitBook v2+ uses main tag or specific classes
        content_selectors = [
            ("main", {}),
            ("div", {"class": lambda x: x and "page-inner" in x}),
            ("div", {"class": lambda x: x and "markdown-section" in x}),
            ("article", {}),
        ]

        for tag, attrs in content_selectors:
            content = soup.find(tag, attrs)
            if content:
                return content

        # Fallback to body if nothing found
        return soup.find("body")

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for GitBook parser.

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

    def parse(self, soup: BeautifulSoup) -> str:
        """Extract and clean text content from GitBook HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Cleaned markdown content as a string

        Usage: `text = parser.parse(soup)` -> markdown text
        """
        # Try to find the main content area
        content = None

        # GitBook v2+ uses main tag or specific classes
        content_selectors = [
            ("main", {}),
            ("div", {"class": lambda x: x and "page-inner" in x}),
            ("div", {"class": lambda x: x and "markdown-section" in x}),
            ("article", {}),
        ]

        for tag, attrs in content_selectors:
            content = soup.find(tag, attrs)
            if content:
                break

        # Fallback to body if nothing found
        if not content:
            content = soup.find("body")

        if not content:
            return ""

        # Remove navigation, sidebars, and other UI elements
        for element in content.find_all(["nav", "header", "footer", "aside"]):
            element.decompose()

        # Remove GitBook-specific UI elements
        for class_name in [
            "navigation",
            "book-summary",
            "book-header",
            "toolbar",
            "page-wrapper",
        ]:
            for element in content.find_all(class_=lambda x: x and class_name in x):  # pyright: ignore[reportCallIssue]
                element.decompose()

        # Filter out sections with high link ratios
        for section in content.find_all(["div", "section"]):
            if self._get_link_ratio(section) > self.exclude_links_ratio:
                section.decompose()

        if self._get_link_ratio(content) <= self.exclude_links_ratio:
            return self._to_markdown(content)
        else:
            return ""
