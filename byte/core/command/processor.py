from byte.core.command.registry import command_registry


class CommandProcessor:
    """Processes user input and routes commands to appropriate handlers.

    Distinguishes between slash commands (/add, /drop) and regular chat input,
    automatically including file context for non-command input to provide
    relevant context to the AI assistant.
    """

    def __init__(self, container):
        # Container provides access to file service and other dependencies
        self.container = container

    async def process_input(self, user_input: str) -> None:
        """Process user input and execute commands if applicable.

        Routes slash commands to command handlers, while regular input gets
        enhanced with file context for better AI responses.
        Usage: `await processor.process_input("/add file.py")` or `await processor.process_input("How do I fix this bug?")`
        """
        user_input = user_input.strip()

        if user_input.startswith("/"):
            await self._process_slash_command(user_input[1:])
        else:
            # Enhance regular input with file context for better AI responses
            await self._process_regular_input(user_input)

    async def _process_slash_command(self, command_text: str) -> None:
        """Parse and execute slash commands with their arguments.

        Splits command name from arguments and delegates to registered command handlers.
        """
        if " " in command_text:
            cmd_name, args = command_text.split(" ", 1)
        else:
            cmd_name, args = command_text, ""

        command = command_registry.get_slash_command(cmd_name)
        console = self.container.make("console")

        if command:
            await command.execute(args)
        else:
            console.print(f"[error]Unknown slash command: /{cmd_name}[/error]")

    async def _process_regular_input(self, user_input: str) -> None:
        """Process regular chat input with file context enhancement."""
        file_service = self.container.make("file_service")
        console = self.container.make("console")

        context = file_service.generate_context_prompt()
        if context:
            full_input = f"{context}\n\nUser input: {user_input}"
            console.print(f"Processing with context:\n{full_input}")
        else:
            console.print(f"Regular input: {user_input}")
