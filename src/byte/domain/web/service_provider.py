from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.web import ChromiumService


class WebServiceProvider(ServiceProvider):
    """Service provider for web browser automation and interaction.

    Registers the Chromium service for headless browser operations,
    web scraping, and page interaction capabilities.
    Usage: Register with container to enable web automation features
    """

    def services(self) -> List[Type[Service]]:
        return [ChromiumService]
