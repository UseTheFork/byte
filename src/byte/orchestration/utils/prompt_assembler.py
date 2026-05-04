import asyncio
from typing import TYPE_CHECKING, TypeVar

from langchain_core.messages import BaseMessage, HumanMessage

from byte.llm import ModelSchema
from byte.orchestration import BaseState, Leaf
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte import Application
    from byte.node import BaseAgentNode

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

    def boot(self, agent_node: BaseAgentNode | None, state: BaseState, **kwargs):

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

    def get_app(self) -> Application:
        return self.app

    def get_state(self) -> BaseState:
        return self.prompt_state

    def get_agent_node(self) -> BaseAgentNode:
        return self.agent_node

    def get_model_schema(self) -> ModelSchema:
        return self.model_schema

    async def generate_messages(self) -> dict:
        templates = {
            "system_message": self.agent_node.get_system_template(),
            "user_message": self.agent_node.get_user_template(),
        }

        if self.agent_node.get_context_template() is not None:
            templates["context_message"] = self.agent_node.get_context_template()

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

        system_message = list_to_multiline_text(built["system_message"])
        user_message = list_to_multiline_text(built["user_message"])

        if self.agent_node.get_context_template() is not None:
            context_message = [HumanMessage(list_to_multiline_text(built["context_message"]))]
        else:
            context_message = []

        return {
            "system_message": system_message,
            "user_message": user_message,
            "context_message": context_message,
            "scratch_messages": self.generate_scratch_state(),
        }

    # async def generate_messages(self) -> dict:
    #     # TODO: We should make this async gather
    #     return {
    #         "system_message": self.assemble_message(self.agent_node.get_system_template()),
    #         "user_message": self.assemble_message(self.agent_node.get_user_template()),
    #         "scratch_messages": self.generate_scratch_state(),
    #         "context_message": self.generate_refreshed_context_state(),
    #     }

    # def generate_refreshed_context_state(self) -> str:
    #     """ """
    #     refreshed_context_message = list_to_multiline_text(
    #         [
    #             self.prompt_state["loaded_skills"],
    #             self.prompt_state["project_context"],
    #             self.prompt_state["project_environment"],
    #             Section.start(SectionType.PROJECT_FILES),
    #             "Below is the current state of the project. It includes all your changes as a result of previous tool calls that have been masked for brevity.",
    #             "",
    #             Section.important("You MUST trust this information as the current state of the files etc."),
    #             "",
    #             self.prompt_state["file_context"],
    #             "",
    #             Section.end(),
    #             self.prompt_state["plan"],
    #             self.epilogue(),
    #         ]
    #     )

    #     return refreshed_context_message

    def generate_scratch_state(self) -> list[BaseMessage]:
        """ """

        return self.prompt_state.get("scratch_messages", [])
