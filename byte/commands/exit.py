from byte.core.command.registry import Command, command_registry


class ExitCommand(Command):
    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit ByteSmith"

    async def execute(self, args: str) -> str:
        # This will be handled specially in the main loop
        return "EXIT_REQUESTED"


command_registry.register_slash_command(ExitCommand())
