from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class GitHubParser(BaseWebParser):
    """Parser for GitHub repository pages and documentation.

    Extracts README content, file contents, and other repository information
    from GitHub pages while filtering out navigation and UI elements.
    """

    def boot(self, exclude_links_ratio: float = 0.5, **kwargs) -> None:
        """Initialize the GitHub parser.

        Args:
                exclude_links_ratio: Threshold for excluding sections with too many links
        """
        self.exclude_links_ratio = exclude_links_ratio

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a GitHub page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this is a GitHub page, False otherwise

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        # Check URL pattern
        if "github.com" in url:
            return True

        # Check for GitHub-specific meta tags
        meta_tags = soup.find_all("meta", property="og:site_name")
        for tag in meta_tags:
            if tag.get("content") == "GitHub":
                return True

        # Check for GitHub-specific elements
        if soup.find("div", {"data-hpc": True}):
            return True

        return False

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from GitHub HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        # README content
        readme = soup.find("article", class_="markdown-body")
        if readme:
            return readme

        # File content view
        file_content = soup.find("div", {"data-target": "react-app.reactRoot"})
        if file_content:
            return file_content

        # Repository about section
        about = soup.find("div", class_="BorderGrid-cell")
        if about:
            return about

        # Fallback to main element
        main = soup.find("main")
        if main:
            return main

        # Last resort: use body
        return soup.find("body")

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for GitHub parser.

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
        """Extract and clean text content from GitHub HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Cleaned text content as a string

        Usage: `text = parser.parse(soup)` -> cleaned text
        """
        # Try to find the main content area
        content = None

        # README content
        readme = soup.find("article", class_="markdown-body")
        if readme:
            content = readme

        # File content view
        if not content:
            file_content = soup.find("div", {"data-target": "react-app.reactRoot"})
            if file_content:
                content = file_content

        # Repository about section
        if not content:
            about = soup.find("div", class_="BorderGrid-cell")
            if about:
                content = about

        # Fallback to main element
        if not content:
            content = soup.find("main")

        # Last resort: use body
        if not content:
            content = soup.find("body")

        if not content:
            return ""

        # Remove navigation, headers, footers, and other UI elements
        for element in content.find_all(
            [
                "nav",
                "header",
                "footer",
                "aside",
            ]
        ):
            element.decompose()

        # Remove GitHub-specific UI elements
        for class_name in [
            "Header",
            "footer",
            "AppHeader",
            "react-code-view-header",
            "react-code-view-bottom-padding",
        ]:
            for element in content.find_all(class_=class_name):
                element.decompose()

        # Filter out sections with high link ratios (likely navigation)
        for section in content.find_all(["div", "section"]):
            if self._get_link_ratio(section) > self.exclude_links_ratio:
                section.decompose()

        return self._to_markdown(content)
