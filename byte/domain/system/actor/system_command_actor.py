from rich.console import Console

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.command.registry import CommandRegistry
from byte.domain.system.actor.coordinator_actor import CoordinatorActor


class SystemCommandActor(Actor):
    async def handle_message(self, message: Message):
        if message.type == MessageType.DOMAIN_COMMAND:
            await self._handle_system_command(message)
        elif message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def _handle_system_command(self, message: Message):
        command = message.payload["command"]

        if command == "exit":
            await self._handle_exit_command()
        elif command == "help":
            await self._handle_help_command()
        else:
            await self._handle_unknown_command(command)

    async def _handle_exit_command(self):
        """Handle the exit command by initiating shutdown"""
        # Send shutdown message to coordinator
        await self.send_to(
            CoordinatorActor,
            Message(type=MessageType.SHUTDOWN, payload={"reason": "user_exit_command"}),
        )

        # Notify command completion (coordinator will handle this before shutdown)
        await self.send_to(
            CoordinatorActor,
            Message(
                type=MessageType.COMMAND_COMPLETED, payload={"command_name": "exit"}
            ),
        )

    async def _handle_help_command(self):
        """Handle the help command"""
        # Get command registry and show help
        command_registry = await self.make(CommandRegistry)
        console = await self.make(Console)

        slash_commands = command_registry._slash_commands
        help_text = "Available commands:\n\n"

        if slash_commands:
            help_text += "Slash commands:\n"
            for name, cmd in slash_commands.items():
                help_text += f"  /{name} - {cmd.description}\n"

        console.print(help_text.strip())

        # Notify command completion
        await self.send_to(
            CoordinatorActor,
            Message(
                type=MessageType.COMMAND_COMPLETED, payload={"command_name": "help"}
            ),
        )

    async def _handle_unknown_command(self, command_name: str):
        console = await self.make(Console)
        console.print(f"[red]Unknown system command: /{command_name}[/red]")

        # Notify command failure
        await self.send_to(
            CoordinatorActor,
            Message(
                type=MessageType.COMMAND_FAILED,
                payload={
                    "command_name": command_name,
                    "error": f"Unknown command: {command_name}",
                },
            ),
        )

    async def setup_subscriptions(self, message_bus: MessageBus):
        message_bus.subscribe(SystemCommandActor, MessageType.DOMAIN_COMMAND)
        message_bus.subscribe(SystemCommandActor, MessageType.SHUTDOWN)
