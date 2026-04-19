from typing import List, Type

from bs4 import BeautifulSoup
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions

from byte import Service
from byte.tui import Messages
from byte.web.exceptions import WebNotEnabledException
from byte.web.parser.base import BaseWebParser
from byte.web.parser.generic_parser import GenericParser
from byte.web.parser.gitbook_parser import GitBookParser
from byte.web.parser.github_parser import GitHubParser
from byte.web.parser.mkdocs_parser import MkDocsParser
from byte.web.parser.raw_content_parser import RawContentParser
from byte.web.parser.sphinx_parser import SphinxParser
from byte.web.service.content_cleaner import ContentCleaner


class ChromiumService(Service):
    """Domain service for web scraping using headless Chrome browser.

    Provides utilities for fetching web pages and converting HTML content
    to markdown format using BeautifulSoup and markdownify.
    Usage: `markdown = await chromium_service.do_scrape("https://example.com")` -> scraped content as markdown
    """

    def boot(self) -> None:
        """Initialize the service with available parsers."""
        self.parsers: List[Type[BaseWebParser]] = [
            SphinxParser,
            GitBookParser,
            GitHubParser,
            MkDocsParser,
            GenericParser,
            RawContentParser,
        ]

    async def do_scrape(self, url: str) -> str:
        """Scrape a webpage and convert it to markdown format.

        Args:
                url: The URL to scrape

        Returns:
                Markdown-formatted content from the webpage

        Raises:
                WebNotEnabledException: If web commands are not enabled in config

        Usage: `content = await chromium_service.do_scrape("https://example.com")` -> markdown string
        """
        # Check if web commands are enabled in configuration
        if not self.app["config"].web.enable:
            raise WebNotEnabledException

        options = ChromiumOptions()
        options.add_argument("--headless=new")
        options.binary_location = str(self.app["config"].web.chrome_binary_location)
        options.start_timeout = 20

        async with Chrome(options=options) as browser:
            await self.emit_tui(Messages.LoadingIndicatorShow("Opening browser..."))
            tab = await browser.start()

            await self.emit_tui(Messages.LoadingIndicatorShow(f"Loading {url}..."))
            await tab.go_to(url)

            await self.emit_tui(Messages.LoadingIndicatorShow("Extracting content..."))
            html_content = await tab.execute_script("return document.documentElement.outerHTML")

            await self.emit_tui(Messages.LoadingIndicatorShow("Converting to markdown..."))
            html_content = html_content.get("result", {}).get("result", {}).get("value", "")

            soup = BeautifulSoup(
                html_content,
                "html.parser",
            )

            # Try to find a suitable parser for this content
            text_content = ""
            for parser_class in self.parsers:
                parser = self.app.make(parser_class)
                if parser.can_parse(soup, url):
                    await self.emit_tui(Messages.LoadingIndicatorShow(f"Parsing with {parser.__class__.__name__}..."))
                    self.app["log"].info(f"Parsing with {parser.__class__.__name__}...")

                    # Extract content element
                    element = parser.extract_content_element(soup)
                    if element is not None:
                        # Apply cleaning pipeline
                        cleaner = self.app.make(ContentCleaner)
                        config = parser.get_cleaning_config()
                        text_content = cleaner.apply_pipeline(element, **config)

                        if text_content.strip():
                            self.app["log"].info(f"Parsed successfully with {parser.__class__.__name__}...")
                            break

            await self.emit_tui(Messages.LoadingIndicatorHide())
            return text_content
