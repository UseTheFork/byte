from bs4 import BeautifulSoup
from markdownify import markdownify as md
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions

from byte.core.service.base_service import Service


class ChromiumService(Service):
    """Domain service for web scraping using headless Chrome browser.

    Provides utilities for fetching web pages and converting HTML content
    to markdown format using BeautifulSoup and markdownify.
    Usage: `markdown = await chromium_service.do_scrape("https://example.com")` -> scraped content as markdown
    """

    async def boot(self, **kwargs):
        pass

    async def do_scrape(self, url: str) -> str:
        """Scrape a webpage and convert it to markdown format.

        Args:
            url: The URL to scrape

        Returns:
            Markdown-formatted content from the webpage

        Usage: `content = await chromium_service.do_scrape("https://example.com")` -> markdown string
        """
        options = ChromiumOptions()
        options.add_argument("--headless=new")
        options.binary_location = (
            "/etc/profiles/per-user/sincore/bin/google-chrome-stable"
        )
        options.start_timeout = 20

        async with Chrome(options=options) as browser:
            tab = await browser.start()
            await tab.go_to(url)

            html_content = await tab.execute_script("return document.body.innerHTML")

            html_content = (
                html_content.get("result", {}).get("result", {}).get("value", "")
            )

            soup = BeautifulSoup(
                html_content,
                "html.parser",
            )
            markdown_content = md(str(soup))

            return markdown_content
