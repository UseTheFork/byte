import asyncio
from typing import TYPE_CHECKING, Optional, Type, TypeVar

if TYPE_CHECKING:
    from byte.container import Container

T = TypeVar("T")


class Bootable:
    _is_booted = False
    container: Optional["Container"]

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        super().__init__()

    async def _boot_mixins(self, **kwargs) -> None:
        """Automatically boot all mixins that have boot_{mixin_name} methods."""
        for cls in self.__class__.__mro__:
            # Get the class name in lowercase for boot method naming
            class_name = cls.__name__.lower()
            boot_method_name = f"boot_{class_name}"

            # Check if this class (not inherited) defines a boot method
            if hasattr(self, boot_method_name) and boot_method_name in cls.__dict__:
                boot_method = getattr(self, boot_method_name)
                if callable(boot_method):
                    if asyncio.iscoroutinefunction(boot_method):
                        await boot_method(**kwargs)
                    else:
                        boot_method(**kwargs)

    async def _async_init(self, **kwargs) -> None:
        """Handle async initialization after container is set."""
        if self._is_booted:
            return

        await self._boot_mixins(**kwargs)
        await self.boot(**kwargs)
        self._is_booted = True

    async def ensure_booted(self, **kwargs) -> None:
        """Ensure this service is booted before use."""
        if not self._is_booted:
            await self._async_init(**kwargs)

    async def boot(self, *args, **kwargs) -> None:
        """Boot method called after initialization.

        Override this method to perform setup that requires the container
        to be fully initialized, such as registering event listeners or
        accessing other services. Called automatically after initialization.
        Usage: `async def boot(self): self.event_dispatcher = await
        self.container.make("event_dispatcher")`
        """
        pass

    async def make(self, service_class: Type[T], **kwargs) -> T:
        """Resolve a service from the container.

        Usage: `service = await self.make(ServiceClass)`
        """
        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")
        return await self.container.make(service_class, **kwargs)
