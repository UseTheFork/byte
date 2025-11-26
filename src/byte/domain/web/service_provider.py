from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.web.service.chromium_service import ChromiumService


class WebServiceProvider(ServiceProvider):
    """Service provider for web browser automation and interaction.

    Registers the Chromium service for headless browser operations,
    web scraping, and page interaction capabilities.
    Usage: Register with container to enable web automation features
    """

    def services(self) -> List[Type[Service]]:
        return [ChromiumService]
