import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.orchestration import WorkflowService
from byte.research import ResearchWorkflow
from byte.tui import InteractionService, Messages
from byte.tui.schemas import Answer


class ResearchCommand(Command):
    """Command to execute the Research agent for general questions and assistance.

    Allows users to ask questions or request assistance from the AI agent,
    processing natural language queries through the agent service.
    Usage: `/research How do I implement error handling?` -> executes Research agent
    """

    @property
    def name(self) -> str:
        return "research"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Ask the AI agent a question or request assistance",
        )
        parser.add_argument("research_query", nargs=argparse.REMAINDER, help="The user's question or query text")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the Research agent with the provided user query.

        Processes the user's question through the agent service, which handles
        the complete interaction flow including AI response generation and display.
        """

        answer_options = [
            Answer(label="AAA", value="AAA", is_default=False),
            Answer(label="B", value="B", is_default=False),
            Answer(label="C", value="C", is_default=False),
        ]

        interaction_service = self.app.make(InteractionService)

        selected = await interaction_service.multi_select("test", answer_options)
        self.app["log"].info(selected)

        research_workflow = self.app.make(ResearchWorkflow)

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(research_workflow, {"user_request": raw_args})

        self.emit_tui(Messages.CommandExecutionCompleted())
