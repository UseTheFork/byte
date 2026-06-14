import asyncio
import re
from typing import TYPE_CHECKING, List, Type, TypeVar

from langchain_core.messages import BaseMessage

from byte.llm import ModelSchema
from byte.orchestration import Leaf, PhaseModel, PhaseUtils
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text
from byte.tools.service.tool_registry_service import ToolRegistryService

if TYPE_CHECKING:
    from byte import Application
    from byte.node import BaseAgentNode
    from byte.orchestration import BaseState
    from byte.tools import BaseTool

T = TypeVar("T")


class PromptAssembler(Bootable, Eventable):
    """Assemble prompts from templates by gathering context from various services."""

    def boot(self, agent_node: BaseAgentNode | None, state: BaseState, extra: dict | None = None, **kwargs) -> None:

        if agent_node is None:
            raise ValueError("agent_node is required and cannot be empty")

        self.agent_node = agent_node
        user_template = agent_node.get_user_template()
        if user_template is None or len(user_template) == 0:
            raise ValueError("user template is required and cannot be empty")

        self.user_template = user_template

        system_template = agent_node.get_system_template()
        if system_template is None or len(system_template) == 0:
            raise ValueError("system template is required and cannot be empty")

        self.system_template = system_template

        self.context_template = agent_node.get_context_template()

        model_schema, _ = self.agent_node.get_model()
        self.model_schema = model_schema

        self.prompt_state = state

        self.assembled_state = {}

        # TODO: this needs to be done better.
        self.merged_state = {**state, **extra}

    def get_app(self) -> Application:
        """Retrieve the application instance."""
        return self.app

    def get_state(self) -> BaseState:
        """Retrieve the current prompt state."""
        return self.prompt_state

    def get_agent_node(self) -> BaseAgentNode:
        """Retrieve the agent node."""
        return self.agent_node

    def get_model_schema(self) -> ModelSchema:
        """Retrieve the model schema."""
        return self.model_schema

    def get_assembled_state(self) -> dict:
        """Retrieve the assembled prompt state."""
        return self.assembled_state

    def get_tools(self) -> List[Type[BaseTool]]:
        """Collect tools from the phase and agent node."""
        tool_schemas = []
        tool_registry_service = self.app.make(ToolRegistryService)

        # Find the first pending step (if any)
        pending_phase = PhaseUtils.get_pending_phase(self.prompt_state)

        if pending_phase is not None and isinstance(pending_phase, PhaseModel):
            # Append any step-specific tools
            if pending_phase.tools:
                for tool_class in pending_phase.tools:
                    tool = tool_registry_service.get_tool(tool_class.name)
                    tool_schemas.append(tool)

        # Bind agent-level tools if provided
        agent_tools = self.get_agent_node().get_tools(self.merged_state)
        if agent_tools:
            tool_schemas.extend(agent_tools)

        return tool_schemas

    async def generate_messages(self) -> dict:
        """Assemble system, user, and context messages from templates and leaves."""
        templates = {
            "system_message": self.agent_node.get_system_template(),
            "user_message": self.agent_node.get_user_template(),
            "context_message": self.agent_node.get_context_template(),
        }

        # Collect all leaves across all templates
        leaf_tasks: list[tuple[str, int, Leaf]] = []  # (template_key, index, leaf)

        for key, template in templates.items():
            for i, item in enumerate(template):
                if isinstance(item, Leaf):
                    leaf_tasks.append((key, i, item))

        # Gather all leaf assemblies concurrently
        assembled = await asyncio.gather(*(leaf.assemble(self) for _, _, leaf in leaf_tasks))

        # Build mutable copies of each template with leaves replaced by their assembled strings
        built: dict[str, list[str]] = {key: list(template) for key, template in templates.items()}

        for (key, idx, _), result in zip(leaf_tasks, assembled):
            built[key][idx] = result

        system_message = self.assemble_message(built["system_message"])
        user_message = self.assemble_message(built["user_message"])
        context_message = self.assemble_message(built["context_message"])

        self.assembled_state = {
            "system_message": system_message,
            "user_message": user_message,
            "context_message": context_message,
        }

        return self.assembled_state

    def assemble_message(self, template: list[str]) -> str:
        """Replace placeholder tokens in template with values from state."""

        result_lines = []
        placeholder_pattern = r"^\{([^}]+)\}$"

        for line in template:
            match = re.match(placeholder_pattern, line)
            if match:
                # Line contains only a placeholder
                key = match.group(1)
                if key in self.merged_state:
                    # Replace with the value
                    value = self.merged_state[key]
                    result_lines.append(value if isinstance(value, str) else str(value))
                # If key not in prompt_state, skip this line (remove it)
            else:
                # Not a placeholder line, keep as-is
                result_lines.append(line)

        return list_to_multiline_text(result_lines)

    def generate_scratch_state(self) -> list[BaseMessage]:
        """Retrieve scratch messages from the current state."""

        return self.prompt_state.get("scratch_messages", [])
