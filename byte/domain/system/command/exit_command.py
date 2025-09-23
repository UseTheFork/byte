from byte.core.actors.message import Message, MessageBus, MessageType
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.system.actor.coordinator_actor import CoordinatorActor


class ExitCommand(Command):
    """Command to gracefully shutdown the Byte application.

    Sends a shutdown message to the coordinator actor to initiate
    a clean application exit with proper resource cleanup.
    Usage: `/exit` -> terminates the application
    """

    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit the Byte application gracefully"

    async def execute(self, args: str) -> None:
        """Execute the exit command by sending shutdown message to coordinator.

        Usage: Called automatically when user types `/exit`
        """

        message_bus = await self.make(MessageBus)

        await message_bus.send_to(
            CoordinatorActor,
            Message(type=MessageType.SHUTDOWN, payload={"reason": "user_exit_command"}),
        )
