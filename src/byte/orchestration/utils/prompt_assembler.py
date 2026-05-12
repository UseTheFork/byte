import asyncio
import re
from typing import TYPE_CHECKING, List, Type, TypeVar

from langchain_core.messages import BaseMessage

from byte.llm import ModelSchema
from byte.orchestration import Leaf
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text
from byte.tools.service.tool_registry_service import ToolRegistryService

if TYPE_CHECKING:
    from byte import Application
    from byte.node import BaseAgentNode
    from byte.orchestration import BaseState
    from byte.plan import PlanStep
    from byte.tools import BaseTool

T = TypeVar("T")


class PromptAssembler(Bootable, Eventable):
    """Assembles prompts from templates by gathering context from various services.

    Coordinates collection of file context, project hierarchy, constraints,
    reinforcement messages, and other prompt components, then assembles them
    into a complete prompt using template replacement.

    Usage: `assembler = PromptAssembler(template=["Hello {name}"])`
    Usage: `state = await assembler.generate_state(state, config, context)`
    Usage: `prompt = assembler.assemble(name="World", age=30)`
    """

    def boot(self, agent_node: BaseAgentNode | None, state: BaseState, extra: dict = {}, **kwargs):

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
        return self.app

    def get_state(self) -> BaseState:
        return self.prompt_state

    def get_agent_node(self) -> BaseAgentNode:
        return self.agent_node

    def get_model_schema(self) -> ModelSchema:
        return self.model_schema

    def get_assembled_state(self) -> dict:
        return self.assembled_state

    def get_tools(self) -> List[Type[BaseTool]]:
        tool_schemas = []
        tool_registry_service = self.app.make(ToolRegistryService)

        plan: list[PlanStep] = self.merged_state.get("plan") or []

        # Find the first pending step (if any)
        pending_step = next((s for s in plan if s.status == "pending"), None)

        if pending_step is not None:
            # Append the required completion tool
            if pending_step.completion_mode == "auto":
                completion_tool = tool_registry_service.get_tool("complete_plan_step")
            else:
                completion_tool = tool_registry_service.get_tool("confirm_complete_plan_step")

            tool_schemas.append(completion_tool)

            # Append any step-specific tools
            if pending_step.tools:
                for tool_class in pending_step.tools:
                    tool = tool_registry_service.get_tool(tool_class.name)
                    tool_schemas.append(tool)

        else:
            # No pending steps remain; if plan exists and all are completed/blocked, allow complete_turn
            if plan and all(s.status in ("completed", "blocked") for s in plan):
                complete_turn_tool = tool_registry_service.get_tool("complete_turn")
                tool_schemas.append(complete_turn_tool)

        # Bind agent-level tools if provided
        agent_tools = self.get_agent_node().get_tools(self.merged_state)
        if agent_tools:
            tool_schemas.extend(agent_tools)

        return tool_schemas

    async def generate_messages(self) -> dict:
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
        """Replace {placeholder} tokens in template with provided values.

        Automatically removes lines containing only placeholders that don't have corresponding values.
        Placeholders are expected to be on their own line with nothing else.

        Usage: `assembler.assemble_system_message(name="World", age=30)`
        """

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
        """ """

        return self.prompt_state.get("scratch_messages", [])
