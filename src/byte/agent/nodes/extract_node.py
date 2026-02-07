from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel, Field

from byte.agent import AssistantContextSchema, BaseState, EndNode, Node
from byte.parsing import ParsingService, ValidationError
from byte.support import Str
from byte.support.mixins import UserInteractive
from byte.support.utils import extract_content_from_message, get_last_message, list_to_multiline_text


class SessionContextFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""

    name: str = Field(
        description="Research findings document name (e.g., 'authentication_patterns', 'error_handling_conventions')"
    )
    content: str = Field(
        description="Detailed research findings including file references, code examples, patterns, and recommendations"
    )


class ExtractNode(Node, UserInteractive):
    """Extract and format content from assistant responses into structured output.

    Processes the last message from the assistant and formats it according to
    the specified schema. Supports plain text extraction or structured session
    context formatting for research findings.

    Usage: `node = await container.make(ExtractNode, schema="session_context")`
    """

    def boot(
        self,
        parsing_service: ParsingService | None = None,
        goto: Type[Node] = EndNode,
        **kwargs,
    ):
        """Initialize the extract node with parsing_service and routing configuration.

        Args:
                goto: Next node to route to after extraction (default: "end_node")
                parsing_service: Output format - "text" for plain extraction or "session_context" for structured formatting

        Usage: `await node.boot(parsing_service=ConventionParsingService, goto=EndNode)`
        """
        self.parsing_service = parsing_service
        self.goto = Str.class_to_snake_case(goto)

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["end_node"]]:
        """Execute content extraction based on configured schema.

        Extracts content from the last assistant message and formats it according
        to the schema. For "text" mode, extracts plain content. For "session_context"
        mode, uses the weak model to structure findings into SessionContextFormatter.

        Args:
                state: Current agent state containing messages
                config: Runnable configuration for LLM invocation
                runtime: Runtime context with assistant configuration

        Returns:
                Command to route to next node with extracted content in state

        Usage: Called automatically by LangGraph during graph execution
        """

        last_message = get_last_message(state["scratch_messages"])

        if self.parsing_service is None:
            output = extract_content_from_message(last_message)
            return Command(goto=str(self.goto), update={"extracted_content": output})

        try:
            content = extract_content_from_message(last_message)
            parsed_content = self.parsing_service.parse(content)
            self.app["log"].info(parsed_content)
            return Command(goto=str(self.goto), update={"extracted_content": parsed_content})
        except ValidationError as e:
            error_message = list_to_multiline_text(
                [
                    "Your response is malformed:",
                    "```text",
                    str(e),
                    "```",
                    "Reply with the corrected blocks.",
                    "",
                ]
            )

            return Command(goto="assistant_node", update={"errors": error_message})
