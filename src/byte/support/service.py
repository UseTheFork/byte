from abc import ABC
from typing import Any, TypeVar

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.eventable import Eventable
from byte.core.mixins.injectable import Injectable

T = TypeVar("T")


class Service(ABC, Bootable, Configurable, Injectable, Eventable):
    async def validate(self) -> bool:
        """Validate service state before executing handle method.

        This method is called before handle() to ensure the service is in a valid
        state to perform its operations. Concrete services should override this
        to implement validation logic specific to their requirements.

        Returns:
                True if validation passes, False otherwise.

        Usage: `is_valid = await service.validate()` -> check service state
        """
        return True

    async def handle(self, *args, **kwargs) -> Any:
        """Handle service-specific operations with flexible parameters.

        This method should be implemented by concrete service classes to define
        their core business logic. The kwargs parameter allows for flexible
        parameter passing that can vary between different service implementations.

        Args:
                **kwargs: Flexible keyword arguments specific to the service implementation. Each concrete service should document its expected parameters.

        Returns:
                Service-specific return value as defined by the concrete implementation.
        """
        pass

    async def __call__(self, **kwargs) -> Any:
        """Execute the service by validating then handling.

        Runs validation first, then executes the handle method if validation passes.
        This provides a convenient way to invoke services while ensuring they're
        in a valid state before processing.

        Args:
                **kwargs: Flexible keyword arguments passed to handle method.

        Returns:
                Result from handle method execution.

        Usage: `result = await service(**kwargs)` -> validate and execute service
        """
        await self.validate()
        return await self.handle(**kwargs)
