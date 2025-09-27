import re
from typing import Dict, List, Type, Union

from pydantic import ValidationError

from byte.domain.agent.coder.commands import (
    AddFileCommand,
    BaseCommand,
    ReplaceTextCommand,
)


class CommandParser:
    """Utility class for parsing commands from markdown-formatted agent responses.

    Parses the Final Answer format and creates validated Pydantic command models:
    ---
    # Final Answer

    ## Command
    ```
    command_name
    ```
    ### arg_name
    ```
    arg_value
    ```
    ---
    """

    COMMAND_REGISTRY: Dict[str, Type[BaseCommand]] = {
        "replace_text_in_file": ReplaceTextCommand,
        "add_file": AddFileCommand,
    }

    def parse_commands(self, text: str) -> List[BaseCommand]:
        """Parse commands from markdown text and return validated Pydantic models.

        Args:
            text: The markdown text containing commands

        Returns:
            List of validated BaseCommand instances

        Raises:
            ValueError: If command parsing or validation fails
        """
        commands = []

        # Extract raw command data using existing logic
        raw_commands = self._extract_raw_commands(text)

        for raw_command in raw_commands:
            try:
                command_class = self.COMMAND_REGISTRY.get(raw_command["command"])
                if not command_class:
                    raise ValueError(f"Unknown command: {raw_command['command']}")

                # Create and validate the command model
                command = command_class(**raw_command["args"])
                commands.append(command)

            except ValidationError as e:
                # Convert Pydantic validation errors to readable format
                error_details = []
                for error in e.errors():
                    field = " -> ".join(str(loc) for loc in error["loc"])
                    error_details.append(f"{field}: {error['msg']}")

                raise ValueError(
                    f"Invalid command '{raw_command['command']}': {'; '.join(error_details)}"
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to parse command '{raw_command['command']}': {e}"
                )

        return commands

    def _extract_raw_commands(
        self, text: str
    ) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        """Extract raw command data from markdown text.

        Args:
            text: The markdown text containing commands

        Returns:
            List of dictionaries with 'command' and 'args' keys
        """
        commands = []

        # Find the Final Answer section
        final_answer_match = re.search(
            r"# Final Answer\s*\n(.*?)(?=---|\Z)", text, re.DOTALL
        )
        if not final_answer_match:
            return commands

        final_answer_content = final_answer_match.group(1)

        # Find all command blocks
        command_pattern = r"## Command\s*\n```[^\n]*\n([^\n]+)\n```\s*\n((?:### [^\n]+\s*\n```[^\n]*\n.*?\n```\s*\n?)*)"
        command_matches = re.finditer(command_pattern, final_answer_content, re.DOTALL)

        for match in command_matches:
            command_name = match.group(1).strip()
            args_section = match.group(2)

            # Parse arguments
            args = self._parse_arguments(args_section)

            commands.append({"command": command_name, "args": args})

        return commands

    def _parse_arguments(self, args_section: str) -> Dict[str, str]:
        """Parse arguments from the arguments section.

        Args:
            args_section: The section containing argument definitions

        Returns:
            Dictionary mapping argument names to values
        """
        args = {}

        # Pattern to match ### arg_name followed by ```[language]\nvalue\n```
        arg_pattern = r"### ([^\n]+)\s*\n```[^\n]*\n(.*?)\n```"
        arg_matches = re.finditer(arg_pattern, args_section, re.DOTALL)

        for match in arg_matches:
            arg_name = match.group(1).strip()
            arg_value = match.group(2).strip()
            args[arg_name] = arg_value

        return args
