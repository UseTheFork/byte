import asyncio
from abc import abstractmethod


class Bootable:
    async def _async_init(self) -> None:
        """Handle async initialization after container is set."""
        await self.boot()
        await self._boot_mixins()

    async def _boot_mixins(self) -> None:
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
                        await boot_method()
                    else:
                        boot_method()

    @abstractmethod
    async def boot(self) -> None:
        """Boot method called after initialization.

                Override this method to perform setup that requires the container
                to be fully initialized, such as registering event listeners or
                accessing other services. Called automatically after initialization.
                Usage: `async def boot(self): self.event_dispatcher = await
        self.container.make("event_dispatcher")`
        """
        pass
