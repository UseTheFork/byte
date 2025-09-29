from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.mcp.service.mcp_service import MCPService


class MCPServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [MCPService]
