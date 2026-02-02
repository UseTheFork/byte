from bs4.element import Comment, NavigableString, Tag
from markdownify import markdownify

from byte import Service


class ContentCleaner(Service):
    """Service for cleaning and converting HTML content to markdown.

    Provides a reusable pipeline for processing scraped web content including
    element removal, link density filtering, and markdown conversion.
    Usage: `cleaned = await cleaner.apply_pipeline(soup_element)` -> markdown string
    """

    def boot(self) -> None:
        """Initialize the content cleaner with default settings."""
        pass

    def remove_unwanted_elements(
        self,
        element: Tag,
        tags_to_remove: list[str] | None = None,
    ) -> Tag:
        """Remove unwanted HTML elements like scripts, styles, and navigation.

        Args:
            element: BeautifulSoup element to clean
            tags_to_remove: List of tag names to remove (uses defaults if None)

        Returns:
            Cleaned BeautifulSoup element

        Usage: `cleaned = cleaner.remove_unwanted_elements(soup)` -> cleaned element
        """
        if tags_to_remove is None:
            tags_to_remove = [
                "script",
                "noscript",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
            ]

        for tag in tags_to_remove:
            for el in element.find_all(tag):
                el.decompose()

        return element

    def _get_link_ratio(self, section: Tag) -> float:
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

    def filter_by_link_density(
        self,
        element: Tag,
        max_ratio: float = 0.5,
    ) -> Tag:
        """Remove sections with high link-to-text ratios.

        Args:
            element: BeautifulSoup element to filter
            max_ratio: Maximum allowed ratio of link text to total text (0.0 to 1.0)

        Returns:
            Filtered BeautifulSoup element

        Usage: `filtered = cleaner.filter_by_link_density(soup, 0.5)` -> filtered element
        """
        for section in element.find_all(["div", "section"]):
            if self._get_link_ratio(section) > max_ratio:
                section.decompose()

        return element

    def normalize_whitespace(self, element: Tag) -> Tag:
        """Normalize whitespace in HTML element while preserving structure.

        Args:
            element: BeautifulSoup element to normalize

        Returns:
            Element with normalized whitespace

        Usage: `normalized = cleaner.normalize_whitespace(soup)` -> normalized element
        """
        # This is a placeholder for future whitespace normalization logic
        return element

    def convert_to_markdown(self, element: Tag) -> str:
        """Convert HTML element to markdown format.

        Args:
            element: BeautifulSoup element to convert

        Returns:
            Markdown-formatted string

        Usage: `markdown = cleaner.convert_to_markdown(soup)` -> markdown string
        """
        return markdownify(
            str(element),
            heading_style="ATX",
            bullets="-",
            strip=["script", "style"],
        ).strip()

    def _process_element(self, element, elements_to_skip: list, newline_elements: list) -> str:
        """Traverse through HTML tree recursively to preserve newline and skip unwanted elements.

        Args:
            element: Element to process
            elements_to_skip: List of tag names to skip
            newline_elements: List of tag names that should add newlines

        Returns:
            Processed text content
        """
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

    def get_clean_text(self, element: Tag) -> str:
        """Extract cleaned text with newlines preserved and irrelevant elements removed.

        Args:
            element: BeautifulSoup element to extract text from

        Returns:
            Cleaned text with preserved structure

        Usage: `text = cleaner.get_clean_text(soup)` -> cleaned text
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

    def apply_pipeline(
        self,
        element: Tag,
        remove_unwanted: bool = True,
        filter_links: bool = False,
        link_ratio: float = 0.5,
        normalize: bool = False,
        to_markdown: bool = True,
    ) -> str:
        """Apply a configurable cleaning pipeline to HTML content.

        Args:
            element: BeautifulSoup element to process
            remove_unwanted: Whether to remove scripts, styles, navigation, etc.
            filter_links: Whether to filter sections by link density
            link_ratio: Maximum link-to-text ratio if filter_links is True
            normalize: Whether to normalize whitespace
            to_markdown: Whether to convert to markdown (if False, returns plain text)

        Returns:
            Processed content as string (markdown or plain text)

        Usage: `result = cleaner.apply_pipeline(soup, filter_links=True)` -> cleaned content
        """
        if remove_unwanted:
            element = self.remove_unwanted_elements(element)

        if filter_links:
            element = self.filter_by_link_density(element, link_ratio)

        if normalize:
            element = self.normalize_whitespace(element)

        if to_markdown:
            return self.convert_to_markdown(element)
        else:
            return self.get_clean_text(element)
