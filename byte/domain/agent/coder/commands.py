from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.command.registry import Command


class CoderCommand(Command):
    """Command to interact with the coder agent."""

    @property
    def name(self) -> str:
        return "coder"

    @property
    def description(self) -> str:
        return "Get coding assistance from the specialized coder agent"

    async def execute(self, args: str) -> None:
        """Execute coder request through the actor system."""
        if not args.strip():
            print("Please provide a coding request.")
            print("Usage: /coder <your coding request>")
            return

        # Send message to agent actor instead of handling directly
        message_bus = await self.make(MessageBus)
        await message_bus.send_to(
            "agent",
            Message(
                type=MessageType.USER_INPUT,
                payload={"input": args, "agent_type": "coder"},
            ),
        )
