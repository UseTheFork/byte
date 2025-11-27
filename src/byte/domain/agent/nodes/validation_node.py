from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import extract_content_from_message, get_last_message
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService


class ValidationNode(Node, UserInteractive):
    """Node for validating assistant responses against configured constraints.

    Performs validation checks on the last message content, such as line count limits.
    If validation fails, returns to assistant_node with error messages for correction.

    Usage: `node = await container.make(ValidationNode, max_lines=50)`
    """

    async def boot(
        self,
        goto: str = "end_node",
        max_lines: int | None = None,
        **kwargs,
    ):
        """Initialize the validation node with constraints and routing configuration.

        Args:
                goto: Next node to route to after successful validation (default: "end_node")
                max_lines: Maximum number of non-blank lines allowed in response content (optional)

        Usage: `await node.boot(goto="end_node", max_lines=100)`
        """
        self.max_lines = max_lines
        self.goto = goto

    def _validate_max_lines(self, content: str, validation_errors: list[str]) -> list[str]:
        """Validate that content doesn't exceed max_lines limit.

        Usage: `errors = self._validate_max_lines(content, [])`
        """
        if self.max_lines is None:
            return validation_errors

        lines = [line for line in content.split("\n") if line.strip()]
        line_count = len(lines)

        if line_count > self.max_lines:
            validation_errors.append(f"Content exceeds maximum line limit: {line_count} lines (max: {self.max_lines})")

        return validation_errors

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        """Execute validation checks on the last assistant message.

        Runs configured validation checks (e.g., max_lines) on the message content.
        If any validation fails, returns to assistant_node with error messages.
        Otherwise, proceeds to the configured goto node.

        Args:
                state: Current agent state containing messages
                config: Runnable configuration
                runtime: Runtime context with assistant configuration

        Returns:
                Command to route to assistant_node (on error) or goto node (on success)

        Usage: Called automatically by LangGraph during graph execution
        """
        last_message = get_last_message(state["scratch_messages"])
        message_content = extract_content_from_message(last_message)

        validation_errors: list[str] = []

        if self.max_lines is not None:
            validation_errors = self._validate_max_lines(message_content, validation_errors)

        if validation_errors:
            error_message = "# Fix the following issues:\n" + "\n".join(f"- {error}" for error in validation_errors)

            console = await self.make(ConsoleService)
            console.print_warning_panel(
                f"{len(validation_errors)} validation error(s) found. Requesting corrections.",
                title="Validation Failed",
            )

            return Command(goto="assistant_node", update={"errors": error_message})

        return Command(goto=self.goto)
