from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from bs4.element import Tag
from markdownify import markdownify

from byte.support.mixins import Bootable


class BaseWebParser(ABC, Bootable):
    """Abstract base class for web content parsers.

    Each parser implementation should identify if it can handle specific HTML content
    and provide a method to extract clean text from that content.
    """

    @abstractmethod
    def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
        """Determine if this parser can handle the given HTML content.

        Args:
                soup: BeautifulSoup object containing the HTML content
                url: The URL of the page being parsed

        Returns:
                True if this parser should be used for the content, False otherwise

        Usage: `if parser.can_parse(soup, url)` -> boolean
        """
        pass

    @abstractmethod
    def extract_content_element(self, soup: BeautifulSoup) -> Tag | None:
        """Extract the main content element from the HTML.

        Args:
                soup: BeautifulSoup object containing the HTML content

        Returns:
                BeautifulSoup Tag containing the main content, or None if not found

        Usage: `element = parser.extract_content_element(soup)` -> Tag or None
        """
        pass

    def get_cleaning_config(self) -> dict:
        """Get the cleaning pipeline configuration for this parser.

        Returns:
                Dictionary with cleaning pipeline settings

        Usage: `config = parser.get_cleaning_config()` -> dict
        """
        return {
            "remove_unwanted": True,
            "filter_links": False,
            "link_ratio": 0.5,
            "normalize": False,
            "to_markdown": True,
        }

    def _process_element(self, element, elements_to_skip: list, newline_elements: list) -> str:
        """Traverse through HTML tree recursively to preserve newline and skip unwanted elements.

        Args:
                element: Element to process
                elements_to_skip: List of tag names to skip
                newline_elements: List of tag names that should add newlines

        Returns:
                Processed text content
        """
        from bs4.element import Comment, NavigableString, Tag

        tag_name = getattr(element, "name", None)
        if isinstance(element, Comment) or tag_name in elements_to_skip:
            return ""
        elif isinstance(element, NavigableString):
            return str(element)
        elif tag_name == "br":
            return "\n"
        elif tag_name in newline_elements:
            return (
                "".join(
                    self._process_element(child, elements_to_skip, newline_elements)
                    for child in element.children
                    if isinstance(child, Tag | NavigableString | Comment)
                )
                + "\n"
            )
        else:
            return "".join(
                self._process_element(child, elements_to_skip, newline_elements)
                for child in element.children
                if isinstance(child, Tag | NavigableString | Comment)
            )

    def _get_clean_text(self, element) -> str:
        """Returns cleaned text with newlines preserved and irrelevant elements removed.

        Args:
                element: BeautifulSoup element to extract text from

        Returns:
                Cleaned text with preserved structure
        """

        elements_to_skip = [
            "script",
            "noscript",
            "canvas",
            "meta",
            "svg",
            "map",
            "area",
            "audio",
            "source",
            "track",
            "video",
            "embed",
            "object",
            "param",
            "picture",
            "iframe",
            "frame",
            "frameset",
            "noframes",
            "applet",
            "form",
            "button",
            "select",
            "base",
            "style",
            "img",
        ]

        newline_elements = [
            "p",
            "div",
            "ul",
            "ol",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "pre",
            "table",
            "tr",
        ]

        text = self._process_element(element, elements_to_skip, newline_elements)
        return text.strip()

    def _get_link_ratio(self, section) -> float:
        """Calculate the ratio of link text to total text in a section.

        Args:
                section: BeautifulSoup element to analyze

        Returns:
                Ratio of link text to total text (0.0 to 1.0)
        """
        links = section.find_all("a")
        total_text = "".join(str(s) for s in section.stripped_strings)
        if len(total_text) == 0:
            return 0.0

        link_text = "".join(str(string.string.strip()) for link in links for string in link.strings if string)
        return len(link_text) / len(total_text)

    def _to_markdown(self, element) -> str:
        """Convert HTML element to markdown format.

        Args:
                element: BeautifulSoup element to convert

        Returns:
                Markdown-formatted string
        """
        return markdownify(
            str(element),
            heading_style="ATX",
            bullets="-",
            strip=["script", "style"],
        ).strip()
