from bs4 import BeautifulSoup
from bs4.element import Tag

from byte.web.parser.base import BaseWebParser


class DuckDuckGoLiteParser(BaseWebParser):
    """Parser for DuckDuckGo Lite search results pages.

    Extracts search result entries from DuckDuckGo Lite HTML, including
    titles, snippets, and URLs, while filtering out ads and navigation.
    """

    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this is a DuckDuckGo Lite search results page.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this is a DuckDuckGo Lite search results page, False otherwise

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        return "lite.duckduckgo.com" in url

    def parse(self, soup: BeautifulSoup) -> str:
        """Parse DuckDuckGo Lite search results from the table layout.

        Iterates over the results table rows and extracts the title, URL,
        and snippet for each search result.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                Formatted string with each result's title, URL, and snippet

        Usage: `results = parser.parse(soup)` -> formatted string
        """
        results = []

        table = soup.find("table")
        if table is None:
            return ""

        rows = table.find_all("tr")
        i = 0
        while i < len(rows):
            row = rows[i]

            # Title and URL row — contains an <a class="result-link">
            link_tag = row.find("a", class_="result-link")
            if link_tag:
                title = link_tag.get_text(strip=True)
                url = link_tag.get("href", "")

                # Snippet is in the next row
                snippet = ""
                if i + 1 < len(rows):
                    snippet_cell = rows[i + 1].find("td", class_="result-snippet")
                    if snippet_cell:
                        snippet = snippet_cell.get_text(strip=True)
                        i += 1  # skip the snippet row

                results.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")

            i += 1

        return "\n\n".join(results)

    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main search results container from DuckDuckGo Lite HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the search results table, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        return soup.find("table")

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for DuckDuckGo Lite parser.

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
