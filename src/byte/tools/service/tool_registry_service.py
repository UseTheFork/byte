from typing import TYPE_CHECKING, Dict, List, Optional

from langchain_core.tools.base import BaseTool

from byte.support import Service

if TYPE_CHECKING:
    pass


# TODO: Clean up / Doc strings
class ToolRegistryService(Service):
    """Central registry for"""

    def boot(self):
        # Separate namespaces for different command types
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        """R"""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve a registered"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """Retrieve all tools"""
        all_tools = list(self._tools.values())
        return all_tools
