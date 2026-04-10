from typing import Literal, Type

from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import EndNode, Node
from byte.orchestration import AssistantContextSchema, BaseState, ValidationError, Validator
from byte.support import Str
from byte.support.mixins import UserInteractive
from byte.tui import Messages


class ValidationNode(Node, UserInteractive):
    """Node for validating assistant responses against configured constraints.

    Performs validation checks on the last message content, such as line count limits.
    If validation fails, returns to main_model_node with error messages for correction.

    Usage: `node = await container.make(ValidationNode, max_lines=50)`
    """

    def boot(
        self,
        validators: list[Validator],
        goto: Type[Node] = EndNode,
        **kwargs,
    ):
        """Initialize the validation node with constraints and routing configuration.

        Args:
                goto: Next node to route to after successful validation (default: "end_node")
                max_lines: Maximum number of non-blank lines allowed in response content (optional)

        Usage: `await node.boot(goto="end_node", max_lines=100)`
        """
        self.validators = validators
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["routing_node"]]:
        """Execute validation checks on the last assistant message.

        Runs configured validation checks (e.g., max_lines) on the message content.
        If any validation fails, returns to main_model_node with error messages.
        Otherwise, proceeds to the configured goto node.

        Args:
                state: Current agent state containing messages
                config: Runnable configuration
                runtime: Runtime context with assistant configuration

        Returns:
                Command to route to main_model_node (on error) or goto node (on success)

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

            await self.emit_tui(
                Messages.CreatePanel(
                    f"{len(validation_errors)} validation error(s) found. Requesting corrections.",
                    title="Validation Failed",
                    border_style="warning",
                )
            )

            # This should route to the previous node using the state.
            return self.route_to(self.goto, {"scratch_messages": HumanMessage(error_message)})

        return self.route_to(self.goto)
