from langgraph.graph.state import RunnableConfig

from byte.domain.agent.implementations.coder.edit_format.base import EditFormat
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState
from byte.domain.files.service.file_service import FileService


class SetupNode(Node):
    async def boot(self, edit_format: EditFormat, **kwargs):
        self.edit_format = edit_format

    async def __call__(self, state: BaseState, config: RunnableConfig):
        file_service = await self.make(FileService)
        file_context = file_service.generate_context_prompt()

        return {
            "file_context": file_context,
            "edit_format_system": self.edit_format.prompts.system,
            "examples": self.edit_format.prompts.examples,
            "agent_status": "",
            "errors": [],
        }
