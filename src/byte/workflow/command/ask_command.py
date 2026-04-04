import argparse
from argparse import Namespace

from byte import ByteArgumentParser, Command, EventBus, Events
from byte.tui import Messages
from byte.workflow import AskWorkflow, WorkflowService


class AskCommand(Command):
    """Command to execute the Ask agent for general questions and assistance.

    Allows users to ask questions or request assistance from the AI agent,
    processing natural language queries through the agent service.
    Usage: `/ask How do I implement error handling?` -> executes Ask agent
    """

    @property
    def name(self) -> str:
        return "ask"

    @property
    def category(self) -> str:
        return "Agent"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Ask the AI agent a question or request assistance",
        )
        parser.add_argument("ask_query", nargs=argparse.REMAINDER, help="The user's question or query text")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the Ask agent with the provided user query.

        Processes the user's question through the agent service, which handles
        the complete interaction flow including AI response generation and display.
        """

        ask_workflow = self.app.make(AskWorkflow)
        event_bus = self.app.make(EventBus)
        await event_bus.emit(Events.TuiMessage(Messages.WorkflowStarted()))

        workflow_service = self.app.make(WorkflowService)
        await workflow_service.execute(ask_workflow, raw_args)
