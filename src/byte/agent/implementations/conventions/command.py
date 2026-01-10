from argparse import Namespace

from byte import Console
from byte.agent import ConventionAgent
from byte.agent.implementations.conventions.constants import FOCUS_MESSAGES, ConventionFocus
from byte.cli import ByteArgumentParser, Command
from byte.knowledge import ConventionContextService
from byte.support.mixins import UserInteractive
from byte.support.utils import slugify


class ConventionCommand(Command, UserInteractive):
    """Generate project convention documents by analyzing codebase patterns.

    Prompts user to select convention type (style guide, architecture, etc.),
    invokes the convention agent to analyze the codebase, and saves the
    generated convention document to the conventions directory.
    Usage: `/convention` -> prompts for type and generates convention document
    """

    @property
    def name(self) -> str:
        return "convention"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Generate convention documents by analyzing codebase patterns and saving them to the conventions directory",
        )
        return parser

    async def prompt_convention_type(self) -> str | None:
        """Prompt user to select the type of convention to generate.

        Usage: `convention_type = await self.prompt_convention_type()` -> returns selected convention type
        """

        choices = list(FOCUS_MESSAGES.keys()) + ["Other"]

        return await self.prompt_for_select(
            "What type of convention would you like to generate?", choices, default="Language Style Guide"
        )

    async def prompt_custom_convention(self) -> ConventionFocus | None:
        """Prompt user to enter custom convention details for "Other" type.

        Usage: `focus = await self.prompt_custom_convention()` -> returns ConventionFocus with user input
        """

        focus_message = await self.prompt_for_input("Enter the focus message for this convention:")
        if not focus_message:
            return None

        filename_input = await self.prompt_for_input("Enter a filename for this convention (without extension):")
        if not filename_input:
            return None

        # Create uppercase filename with .md extension
        file_name = f"{slugify(filename_input, '_').upper()}.md"

        return ConventionFocus(focus_message=focus_message, file_name=file_name)

    def get_convention_focus(self, convention_type: str) -> ConventionFocus | None:
        """Get the convention focus configuration for the selected type.

        Usage: `focus = self.get_convention_focus("Language Style Guide")` -> returns ConventionFocus object
        """

        return FOCUS_MESSAGES.get(convention_type)

    async def execute(self, args: Namespace, raw_args: str) -> None:
        convention_type = await self.prompt_convention_type()

        if not convention_type:
            return

        if convention_type == "Other":
            focus = await self.prompt_custom_convention()
        else:
            focus = self.get_convention_focus(convention_type)

        if not focus:
            return

        convention_agent = self.make(ConventionAgent)
        convention: dict = await convention_agent.execute(
            focus.focus_message,
        )

        # Write the convention content to a file
        convention_file_path = self.app.conventions_path(focus.file_name)
        convention_file_path.parent.mkdir(parents=True, exist_ok=True)
        convention_file_path.write_text(convention["extracted_content"])

        # refresh the Conventions in the session by `rebooting` the Service
        convention_context_service = self.make(ConventionContextService)
        convention_context_service.boot()

        console = self.make(Console)
        console.print_success_panel(
            f"Convention document generated and saved to {focus.file_name}\n\nThe convention has been loaded into the session context and is now available for AI reference.",
            title="Convention Generated",
        )
