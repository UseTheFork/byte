from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider

from .handler import ResponseHandler

if TYPE_CHECKING:
    from byte.container import Container


class ResponseServiceProvider(ServiceProvider):
    """Service provider for response handling infrastructure.

    Registers ResponseHandler for centralized agent response processing
    across all domains and commands.
    Usage: Register with container to enable response_handler access
    """

    async def register(self, container: "Container") -> None:
        """Register response handling services in the container."""
        container.singleton(ResponseHandler)

    async def boot(self, container: "Container") -> None:
        """Boot response handling services after all providers are registered."""
        # No additional boot logic needed for response handler
        pass

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return [ResponseHandler]
