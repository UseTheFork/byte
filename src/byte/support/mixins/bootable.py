from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T")


class Bootable:
    _is_booted = False

    def __init__(self, *args, app: Application, **kwargs):
        if app is None:
            raise ValueError("app parameter is required")
        self.app = app
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def _boot_mixins(self, **kwargs) -> None:
        """Automatically boot all mixins that have boot_{mixin_name} methods."""
        for cls in self.__class__.__mro__:
            # Get the class name in lowercase for boot method naming
            class_name = cls.__name__.lower()
            boot_method_name = f"boot_{class_name}"

            # Check if this class (not inherited) defines a boot method
            if hasattr(self, boot_method_name) and boot_method_name in cls.__dict__:
                boot_method = getattr(self, boot_method_name)
                if callable(boot_method):
                    boot_method(**kwargs)

    def ensure_booted(self, **kwargs) -> None:
        """Ensure this service is booted before use."""
        if self._is_booted:
            return

        self._boot_mixins(**kwargs)
        self.boot(**kwargs)
        self._is_booted = True

    def boot(self, *args, **kwargs) -> None:
        """Boot method called after initialization.
        __init__
                Override this method to perform setup that requires the container
                to be fully initialized, such as registering event listeners or
                accessing other services. Called automatically after initialization.
                Usage: `async def boot(self): self.event_dispatcher = await
                self.container.make("event_dispatcher")`
        """
        pass
