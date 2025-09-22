from abc import ABC
from typing import TypeVar

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable, Injectable

T = TypeVar("T")


class Service(ABC, Bootable, Configurable, Injectable):
    async def handle(self, **kwargs):
        """Handle service-specific operations with flexible parameters.

        This method should be implemented by concrete service classes to define
        their core business logic. The kwargs parameter allows for flexible
        parameter passing that can vary between different service implementations.

        Args:
            **kwargs: Flexible keyword arguments specific to the service implementation.
                     Each concrete service should document its expected parameters.

        Returns:
            Service-specific return value as defined by the concrete implementation.
        """
        pass
