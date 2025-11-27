from argparse import Namespace

from pydantic import BaseModel

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import slugify
from byte.domain.agent.implementations.conventions.agent import ConventionAgent
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.service.convention_context_service import ConventionContextService


class ConventionFocus(BaseModel):
    """Configuration for a convention type's focus and output."""

    focus_message: str
    file_name: str


FOCUS_MESSAGES = {
    "Project Tooling": ConventionFocus(
        focus_message=(
            "Generate a project tooling convention focusing on: "
            "build systems and package managers (e.g., npm, composer, yarn, uv), "
            "bundlers and dev tools (e.g., vite, webpack), "
            "task runners, linting and formatting tools, "
            "and tooling configuration standards."
        ),
        file_name="PROJECT_TOOLING.md",
    ),
    "Documentation": ConventionFocus(
        focus_message=(
            "Generate a documentation convention focusing on: "
            "documentation structure and format (e.g., MkDocs), "
            "content organization, writing style and tone, "
            "code example standards, and documentation maintenance practices."
        ),
        file_name="DOCUMENTATION_STANDARDS.md",
    ),
    "Language Style Guide": ConventionFocus(
        focus_message=(
            "Generate a language style guide convention focusing on: "
            "naming conventions, code formatting, type hints, imports, "
            "class and function structure, and language-specific best practices."
        ),
        file_name="LANGUAGE_STYLE_GUIDE.md",
    ),
    "Project Architecture": ConventionFocus(
        focus_message=(
            "Generate a project architecture convention focusing on: "
            "directory structure, module organization, dependency patterns, "
            "separation of concerns, and architectural principles used in this codebase."
        ),
        file_name="PROJECT_ARCHITECTURE.md",
    ),
    "Comment Standards": ConventionFocus(
        focus_message=(
            "Generate a comment standards convention focusing on: "
            "docstring format and requirements, inline comment style, "
            "when to comment vs self-documenting code, and documentation best practices."
        ),
        file_name="COMMENT_STANDARDS.md",
    ),
    "Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a code patterns convention focusing on: "
            "common design patterns used, error handling approaches, "
            "async/await patterns, dependency injection, and recurring code structures."
        ),
        file_name="CODE_PATTERNS.md",
    ),
    "Frontend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a frontend code patterns convention focusing on: "
            "component structure and organization, state management patterns, "
            "UI/UX patterns, event handling, API integration patterns, "
            "and frontend-specific design patterns."
        ),
        file_name="FRONTEND_CODE_PATTERNS.md",
    ),
    "Backend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a backend code patterns convention focusing on: "
            "API design patterns, database access patterns, service layer organization, "
            "authentication and authorization patterns, error handling and logging, "
            "and backend-specific architectural patterns."
        ),
        file_name="BACKEND_CODE_PATTERNS.md",
    ),
}


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

        convention_agent = await self.make(ConventionAgent)
        convention: dict = await convention_agent.execute(
            focus.focus_message,
        )

        # Write the convention content to a file
        convention_file_path = self._config.system.paths.conventions / focus.file_name
        convention_file_path.parent.mkdir(parents=True, exist_ok=True)
        convention_file_path.write_text(convention["extracted_content"])

        # refresh the Conventions in the session by `rebooting` the Service
        convention_context_service = await self.make(ConventionContextService)
        await convention_context_service.boot()
        console = await self.make(ConsoleService)
        console.print_success_panel(
            f"Convention document generated and saved to {focus.file_name}\n\nThe convention has been loaded into the session context and is now available for AI reference.",
            title="Convention Generated",
        )
