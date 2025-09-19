from typing import TYPE_CHECKING

from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.agent.ask.commands import AskCommand
from byte.domain.agent.ask.service import AskAgent
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.files.events import AskRequested

if TYPE_CHECKING:
    from byte.container import Container


class AskServiceProvider(ServiceProvider):
    """ """

    async def register(self, container: "Container") -> None:
        """Register coder agent services in the container.

        Usage: `provider.register(container)` -> binds coder services
        """

        # Register coder service
        container.singleton(AskAgent)

        # Register coder command
        container.bind(AskCommand)

    async def boot(self, container: "Container") -> None:
        """Boot coder services after all providers are registered.

        Usage: `provider.boot(container)` -> coder agent ready for development tasks
        """
        command_registry = await container.make(CommandRegistry)

        # Register coder command for user access
        await command_registry.register_slash_command(await container.make(AskCommand))

        agent = await container.make(AskAgent)
        event_dispatcher = await container.make(EventDispatcher)
        event_dispatcher.listen(AskRequested, listener=agent.execute_watch_request)

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return [AskCommand, AskAgent]
