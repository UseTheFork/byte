from textwrap import dedent

from byte.core.utils import dd, extract_content_from_message, get_last_message
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.research.agent import ResearchAgent
from byte.domain.cli.service.command_registry import Command
from byte.domain.files.service.file_service import FileService
from byte.domain.memory.service.memory_service import MemoryService


class InitilizieCommand(Command):
    """ """

    @property
    def name(self) -> str:
        return "init"

    @property
    def description(self) -> str:
        return ""

    async def execute(self, args: str) -> None:
        """Initialize project style guides by analyzing the codebase.

        Usage: `/init` -> analyzes project files and generates style guides
        """
        # Confirm with user before resetting context and memory
        confirmed = await self.prompt_for_confirmation(
            "Running /init will reset context and memory. Continue?", default=False
        )

        if not confirmed:
            return

        memory_service = await self.make(MemoryService)
        await memory_service.new_thread()

        file_service = await self.make(FileService)
        await file_service.clear_context()

        research_agent = await self.make(ResearchAgent)
        coder_agent = await self.make(CoderAgent)

        # Get all project files for the agent to analyze
        project_files = await file_service.get_project_files()

        # Create a formatted list of files for the agent
        file_list = "\n".join([f"- {file}" for file in sorted(project_files)])

        user_message = dedent(f"""
        Analyzing the codebase to create a comment style guide.

        Here are all the project files available for analysis:
        {file_list}

        **IMPORTANT: Keep the guide to 20-30 lines**""")

        init_message: dict = await research_agent.execute(
            request={"messages": [("user", user_message)]}
        )

        ai_message = get_last_message(init_message)
        message_content = extract_content_from_message(ai_message)

        dd(message_content)

        coder_agent: dict = await coder_agent.execute(
            request={
                "messages": [
                    (
                        "user",
                        dedent(f"""
                        Use the following context to generate a `[project_root]/.byte/conventions/COMMENT_STYLEGUIDE.md`,  `[project_root]/.byte/conventions/[language]_STYLEGUIDE.md`,  `[project_root]/.byte/conventions/PROJECT_TOOLING.md`.
                        Keep each file to AT MOST 30 lines.

                        {message_content}"""),
                    )
                ]
            }
        )
