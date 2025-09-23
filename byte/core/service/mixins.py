import asyncio
from typing import TYPE_CHECKING, Optional, Type, TypeVar, cast

if TYPE_CHECKING:
    from byte.container import Container

T = TypeVar("T")


class Bootable:
    _is_booted = False
    container: Optional["Container"]

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        super().__init__()

    async def ensure_booted(self) -> None:
        """Ensure this service is booted before use."""
        if not self._is_booted:
            await self._async_init()

    async def _async_init(self) -> None:
        """Handle async initialization after container is set."""
        if self._is_booted:
            return

        await self._boot_mixins()
        await self.boot()
        self._is_booted = True

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

    async def boot(self) -> None:
        """Boot method called after initialization.

                Override this method to perform setup that requires the container
                to be fully initialized, such as registering event listeners or
                accessing other services. Called automatically after initialization.
                Usage: `async def boot(self): self.event_dispatcher = await
        self.container.make("event_dispatcher")`
        """
        pass


class Injectable:
    """Mixin that provides direct access to container.make() without context.

    Enables services to resolve dependencies directly through their container
    reference instead of using the global context. Useful for services that
    need to resolve dependencies in non-async contexts or prefer explicit
    dependency resolution.
    Usage: `class MyService(Injectable): dependency = await self.make(SomeService)`
    """

    container: Optional["Container"]

    async def make(self, service_class: Type[T]) -> T:
        """Resolve a service from the container.

        Usage: `service = await self.make(ServiceClass)`
        """
        if not self.container:
            raise RuntimeError(
                "No container available - ensure service is properly initialized"
            )
        return await self.container.make(service_class)


class UserInteractive:
    """Mixin that provides user interaction capabilities through the input actor.

    Enables services to prompt users for input or confirmation through the
    actor system. Handles message routing and response collection automatically.
    Usage: `class MyService(UserInteractive): result = await self.prompt_for_confirmation("Continue?", True)`
    """

    container: Optional["Container"]

    async def prompt_for_input(self):
        """Prompt the user for general input via the input actor.

        Sends a request to the InputActor to display the input prompt,
        returning control to the user for general text input.
        Usage: `await self.prompt_for_input()` -> shows input prompt to user
        """
        from byte.core.actors.message import Message, MessageBus, MessageType
        from byte.domain.cli_input.actor.input_actor import InputActor

        if not self.container:
            raise RuntimeError(
                "No container available - ensure service is properly initialized"
            )

        message_bus = await self.container.make(MessageBus)

        await message_bus.send_to(
            InputActor,
            Message(type=MessageType.REQUEST_USER_INPUT, payload={}),
        )

    async def prompt_for_confirmation(self, message: str, default: bool = True):
        """Prompt the user for yes/no confirmation with a custom message.

        Displays a confirmation dialog and waits for user response with
        automatic timeout handling. Returns the default value on timeout.
        Usage: `confirmed = await self.prompt_for_confirmation("Delete file?", False)`
        """
        from byte.core.actors.message import Message, MessageBus, MessageType
        from byte.domain.cli_input.actor.input_actor import InputActor

        if not self.container:
            raise RuntimeError(
                "No container available - ensure service is properly initialized"
            )

        response_queue = asyncio.Queue()
        message_bus = await self.container.make(MessageBus)

        await message_bus.send_to(
            InputActor,
            Message(
                type=MessageType.REQUEST_USER_CONFIRM,
                payload={
                    "message": message,
                    "default": default,
                },
                reply_to=response_queue,
            ),
        )

        try:
            response = await asyncio.wait_for(response_queue.get(), timeout=30.0)
            return cast(bool, response.payload["input"])
        except TimeoutError:
            return default
