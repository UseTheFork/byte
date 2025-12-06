from typing import List

from bs4 import BeautifulSoup
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from rich.live import Live

from byte.core.service.base_service import Service
from byte.domain.cli.rich.rune_spinner import RuneSpinner
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.web.exceptions import WebNotEnabledException
from byte.domain.web.parser.base import BaseWebParser
from byte.domain.web.parser.generic_parser import GenericParser
from byte.domain.web.parser.gitbook_parser import GitBookParser
from byte.domain.web.parser.github_parser import GitHubParser
from byte.domain.web.parser.mkdocs_parser import MkDocsParser
from byte.domain.web.parser.raw_content_parser import RawContentParser
from byte.domain.web.parser.readthedocs_parser import ReadTheDocsParser


class ChromiumService(Service):
    """Domain service for web scraping using headless Chrome browser.

    Provides utilities for fetching web pages and converting HTML content
    to markdown format using BeautifulSoup and markdownify.
    Usage: `markdown = await chromium_service.do_scrape("https://example.com")` -> scraped content as markdown
    """

    async def boot(self) -> None:
        """Initialize the service with available parsers."""
        self.parsers: List[BaseWebParser] = [
            ReadTheDocsParser(),
            GitBookParser(),
            GitHubParser(),
            MkDocsParser(),
            GenericParser(),
            RawContentParser(),
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
        if not self._config.web.enable:
            raise WebNotEnabledException

        console = await self.make(ConsoleService)

        options = ChromiumOptions()
        options.add_argument("--headless=new")
        options.binary_location = str(self._config.web.chrome_binary_location)
        options.start_timeout = 20

        spinner = RuneSpinner(text=f"Scraping {url}...", size=15)

        with Live(spinner, console=console.console, transient=True, refresh_per_second=20):
            async with Chrome(options=options) as browser:
                spinner.text = "Opening browser..."
                tab = await browser.start()

                spinner.text = f"Loading {url}..."
                await tab.go_to(url)

                spinner.text = "Extracting content..."
                html_content = await tab.execute_script("return document.body.innerHTML")

                spinner.text = "Converting to markdown..."
                html_content = html_content.get("result", {}).get("result", {}).get("value", "")

                soup = BeautifulSoup(
                    html_content,
                    "html.parser",
                )

                # Try to find a suitable parser for this content
                parser = None
                for p in self.parsers:
                    if p.can_parse(soup, url):
                        parser = p
                        break

                spinner.text = f"Parsing with {parser.__class__.__name__}..."
                text_content = parser.parse(soup)  # pyright: ignore[reportOptionalMemberAccess]
                return text_content
