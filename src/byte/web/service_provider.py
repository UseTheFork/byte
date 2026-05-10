from typing import List, Type

from byte import Service, ServiceProvider
from byte.web import ChromiumService, SearchWebTool
from byte.web.service.content_cleaner import ContentCleaner


class WebServiceProvider(ServiceProvider):
    """Service provider for web browser automation and interaction.

    Registers the Chromium service for headless browser operations,
    web scraping, and page interaction capabilities.
    Usage: Register with container to enable web automation features
    """

    def tools(self):
        """"""
        return [
            # keep-sorted start
            SearchWebTool,
            # keep-sorted end
        ]

    def services(self) -> List[Type[Service]]:
        return [
            # keep-sorted start
            ChromiumService,
            ContentCleaner,
            # keep-sorted end
        ]
