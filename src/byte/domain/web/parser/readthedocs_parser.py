from bs4 import BeautifulSoup

from byte.domain.web.parser.base import BaseWebParser


class ReadTheDocsParser(BaseWebParser):
    """Parser for ReadTheDocs documentation sites.

    Extracts main content from ReadTheDocs pages by identifying specific HTML tags
    and filtering out navigation, index pages, and other non-content elements.
    """

    def __init__(self, exclude_links_ratio: float = 1.0):
        """Initialize ReadTheDocs parser.

        Args:
                exclude_links_ratio: The ratio of links:content to exclude pages from.
                        This reduces the frequency at which index pages make their way into results.
                        Recommended: 0.5
        """
        self.exclude_links_ratio = exclude_links_ratio

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a ReadTheDocs page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this appears to be a ReadTheDocs page

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        # Check for common ReadTheDocs indicators
        if "readthedocs" in url.lower():
            return True

        # Check for ReadTheDocs-specific meta tags or classes
        rtd_meta = soup.find("meta", attrs={"name": "generator", "content": lambda x: x and "sphinx" in x.lower()})  # pyright: ignore[reportCallIssue]
        if rtd_meta:
            return True

        # Check for common ReadTheDocs HTML structure
        if soup.find("div", {"role": "main"}) or soup.find("main", {"id": "main-content"}):
            return True

        return False

    def parse(self, soup: BeautifulSoup) -> str:
        """Extract and clean text content from ReadTheDocs HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Cleaned text content as a string

        Usage: `text = parser.parse(soup)` -> cleaned text
        """
        # Default tags to search for main content
        html_tags = [
            ("div", {"role": "main"}),
            ("main", {"id": "main-content"}),
        ]

        element = None

        # Search for main content element
        for tag, attrs in html_tags[::-1]:
            element = soup.find(tag, attrs)  # pyright: ignore[reportCallIssue]
            if element is not None:
                break

        if element is not None and self._get_link_ratio(element) <= self.exclude_links_ratio:
            return self._to_markdown(element)
        else:
            return ""
