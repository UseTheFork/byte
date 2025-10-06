from byte.core.utils import dd
from byte.domain.agent.implementations.initilizie.agent import InitilizieAgent
from byte.domain.cli.service.command_registry import Command
from byte.domain.files.service.file_service import FileService


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

        file_service = await self.make(FileService)

        init_agent = await self.make(InitilizieAgent)

        # Get all project files for the agent to analyze
        project_files = await file_service.get_project_files()

        # Create a formatted list of files for the agent
        file_list = "\n".join([f"- {file}" for file in sorted(project_files)])

        user_message = f"""Begin analyzing the codebase to create style guides.

Here are all the project files available for analysis:

{file_list}

Please analyze the codebase structure and create appropriate style guides."""

        init_message: dict = await init_agent.execute(
            request={"messages": [("user", user_message)]}
        )

        dd(init_message)
