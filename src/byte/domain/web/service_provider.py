from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.web.service.chromium_service import ChromiumService


class WebServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [ChromiumService]
