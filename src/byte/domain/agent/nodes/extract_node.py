from typing import Literal, cast

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel, Field

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import extract_content_from_message, get_last_message
from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

# TODO: This dosent feel like the right place for this.

extract_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    "Act as a content formatter that structures research findings into a standardized format.",
                    Boundary.close(BoundaryType.ROLE),
                    "",
                    Boundary.open(BoundaryType.RULES),
                    "- Extract the research findings from the assistant's response",
                    "- Format the content according to the provided schema",
                    "- Preserve all important details, file references, and code examples",
                    "- Ensure the name is descriptive and follows snake_case convention",
                    "- Keep the content well-structured and readable",
                    Boundary.close(BoundaryType.RULES),
                    "",
                    Boundary.open(BoundaryType.GOAL),
                    "Transform the research agent's response into a structured document that can be",
                    "saved to the session context with a clear name and organized content.",
                    Boundary.close(BoundaryType.GOAL),
                ]
            ),
        ),
        ("placeholder", "{messages}"),
    ]
)


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

    async def boot(
        self,
        goto: str = "end_node",
        schema: Literal["text", "session_context"] = "text",
        **kwargs,
    ):
        """Initialize the extract node with schema and routing configuration.

        Args:
                goto: Next node to route to after extraction (default: "end_node")
                schema: Output format - "text" for plain extraction or "session_context" for structured formatting

        Usage: `await node.boot(goto="end_node", schema="session_context")`
        """
        self.schema = schema
        self.goto = goto

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
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

        if self.schema == "text":
            output = extract_content_from_message(last_message)
            return Command(goto=self.goto, update={"extracted_content": output})

        if self.schema == "session_context":
            weak_model = runtime.context.weak
            # Bind schema to model
            model_with_structure = weak_model.with_structured_output(SessionContextFormatter, include_raw=True)
            runnable = extract_prompt | model_with_structure
            output = await runnable.ainvoke(state, config=config)

            result = cast(AIMessage, output.get("raw"))
            await self._track_token_usage(result, "weak")

        return Command(goto=self.goto, update={"extracted_content": output.get("parsed")})
