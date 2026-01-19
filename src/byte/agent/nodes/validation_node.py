from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, Node, ValidationError, Validator
from byte.support.mixins import UserInteractive


class ValidationNode(Node, UserInteractive):
    """Node for validating assistant responses against configured constraints.

    Performs validation checks on the last message content, such as line count limits.
    If validation fails, returns to assistant_node with error messages for correction.

    Usage: `node = await container.make(ValidationNode, max_lines=50)`
    """

    def boot(
        self,
        validators: list[Validator],
        goto: str = "end_node",
        **kwargs,
    ):
        """Initialize the validation node with constraints and routing configuration.

        Args:
                goto: Next node to route to after successful validation (default: "end_node")
                max_lines: Maximum number of non-blank lines allowed in response content (optional)

        Usage: `await node.boot(goto="end_node", max_lines=100)`
        """
        self.validators = validators
        self.goto = goto

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["end_node", "extract_node", "assistant_node"]]:
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

        validation_errors: list[ValidationError] = []

        # Run all validators
        for validator in self.validators:
            errors = await validator.validate(state)
            validation_errors.extend([error for error in errors if error is not None])

        self.app["log"].debug(validation_errors)

        if validation_errors:
            error_message = "# Fix the following issues:\n" + "\n".join(error.format() for error in validation_errors)

            console = self.app["console"]
            console.print_warning_panel(
                f"{len(validation_errors)} validation error(s) found. Requesting corrections.",
                title="Validation Failed",
            )

            return Command(goto="assistant_node", update={"errors": error_message, "extracted_content": None})

        return Command(goto=str(self.goto))
