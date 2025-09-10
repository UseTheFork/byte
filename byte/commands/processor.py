from byte.commands.registry import command_registry


class CommandProcessor:
    def __init__(self, container):
        self.container = container

    async def process_input(self, user_input: str) -> str:
        """Process user input and execute commands if applicable."""
        user_input = user_input.strip()

        if user_input.startswith("/"):
            return await self._process_slash_command(user_input[1:])
        else:
            # For regular input, include file context
            file_service = self.container.make("file_service")
            context = file_service.generate_context_prompt()
            if context:
                full_input = f"{context}\n\nUser input: {user_input}"
                return f"Processing with context:\n{full_input}"
            else:
                return f"Regular input: {user_input}"

    async def _process_slash_command(self, command_text: str) -> str:
        if " " in command_text:
            cmd_name, args = command_text.split(" ", 1)
        else:
            cmd_name, args = command_text, ""

        command = command_registry.get_slash_command(cmd_name)
        if command:
            return await command.execute(args)
        else:
            return f"Unknown slash command: /{cmd_name}"
