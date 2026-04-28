from typing import List, Type

from langchain_core.tools.base import BaseTool

from byte import Service, ServiceProvider
from byte.web import ChromiumService, SearchWebTool
from byte.web.service.content_cleaner import ContentCleaner


class WebServiceProvider(ServiceProvider):
    """Service provider for web browser automation and interaction.

    Registers the Chromium service for headless browser operations,
    web scraping, and page interaction capabilities.
    Usage: Register with container to enable web automation features
    """

    def tools(self) -> List[Type[BaseTool]]:
        """"""
        return [
            SearchWebTool,
        ]

    def services(self) -> List[Type[Service]]:
        return [ChromiumService, ContentCleaner]
