import asyncio
import random
from typing import List, Type

from bs4 import BeautifulSoup
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.constants import By

from byte import Service
from byte.tui import Messages
from byte.web.exceptions import WebNotEnabledException
from byte.web.parser.base import BaseWebParser
from byte.web.parser.generic_parser import GenericParser
from byte.web.parser.gitbook_parser import GitBookParser
from byte.web.parser.github_parser import GitHubParser
from byte.web.parser.google_search_parser import GoogleSearchParser
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
            self.emit_tui(Messages.Status("loading", "Opening browser..."))
            tab = await browser.start()

            self.emit_tui(Messages.Status("loading", f"Loading {url}..."))
            await tab.go_to(url)

            self.emit_tui(Messages.Status("loading", "Extracting content..."))
            html_content = await tab.execute_script("return document.documentElement.outerHTML")

            self.emit_tui(Messages.Status("loading", "Converting to markdown..."))
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
                    self.emit_tui(Messages.Status("loading", f"Parsing with {parser.__class__.__name__}..."))
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

            self.emit_tui(Messages.Status())
            return text_content

    async def do_search(self, query: str) -> str:
        """ """
        # Check if web commands are enabled in configuration
        if not self.app["config"].web.enable:
            raise WebNotEnabledException

        options = ChromiumOptions()
        options.add_argument("--headless=new")
        options.binary_location = str(self.app["config"].web.chrome_binary_location)
        options.start_timeout = 20

        async with Chrome(options=options) as browser:
            self.emit_tui(Messages.Status("loading", "Opening browser..."))
            tab = await browser.start()

            self.emit_tui(Messages.Status("loading", f"Searching for {query}..."))
            await tab.go_to("https://www.google.com/")

            search_box = await tab.find(tag_name="textarea", name="q")
            self.app["log"].info(search_box)
            await search_box.click(
                x_offset=random.randint(-5, 5),
                y_offset=random.randint(-5, 5),
            )
            await asyncio.sleep(random.uniform(0.2, 0.5))
            await search_box.type_text(query, humanize=True)

            # Click submit with realistic parameters
            submit_button = await tab.find(tag_name="input", type="submit")
            self.app["log"].info(submit_button)

            await asyncio.sleep(random.uniform(0.5, 1.5))

            await submit_button.click(
                x_offset=random.randint(-8, 8),
                y_offset=random.randint(-5, 5),
                hold_time=random.uniform(0.1, 0.2),
            )

            await asyncio.sleep(random.uniform(1.5, 2.5))
            html_content = await tab.execute_script("return document.documentElement.outerHTML")
            self.app["log"].info(html_content)

            dynamic_element = await tab.find_or_wait_element(
                By.ID,
                "search",
                timeout=10,
            )

            self.app["log"].info(dynamic_element)

            self.emit_tui(Messages.Status("loading", "Extracting content..."))
            html_content = await tab.execute_script("return document.documentElement.outerHTML")

            self.emit_tui(Messages.Status("loading", "Converting to markdown..."))
            html_content = html_content.get("result", {}).get("result", {}).get("value", "")

            soup = BeautifulSoup(
                html_content,
                "html.parser",
            )

            # Try to find a suitable parser for this content
            text_content = ""

            parser = self.app.make(GoogleSearchParser)
            self.emit_tui(Messages.Status("loading", f"Parsing with {parser.__class__.__name__}..."))
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

            self.emit_tui(Messages.Status())
            return text_content
