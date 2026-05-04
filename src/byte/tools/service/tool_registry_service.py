from typing import Dict, Optional, Type

from byte.support import Boundary, BoundaryType, Service
from byte.tools.base_tool import BaseTool


class ToolRegistryService(Service):
    """Central registry for tool discovery and instantiation.

    Manages tool registration and provides lookup services for resolving
    tools by name. Tools are stored as classes and instantiated via the
    application container on retrieval.
    """

    def boot(self):
        # Separate namespaces for different command types
        self._tools: Dict[str, Type[BaseTool]] = {}

    def register_tool(self, tool: Type[BaseTool]):
        """Register a tool class by its name.

        Usage: `registry.register_tool(EditFileTool)`
        """
        self._tools[tool.name] = tool

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered by name.

        Usage: `registry.has_tool("edit_file")`
        """
        return name in self._tools

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve and instantiate a registered tool by name.

        Returns:
            An instantiated BaseTool if found, otherwise None.

        Usage: `tool = registry.get_tool("edit_file")`
        """
        tool_class = self._tools.get(name)
        if tool_class is None:
            return None
        return self.app.make(tool_class)

    def tools_to_prompt_xml(self, tools: Optional[dict[str, Type[BaseTool]]] = None) -> str:
        """Format a dict of tools as XML for injection into a prompt."""
        if tools is None:
            tools = self._tools

        if not tools:
            return ""

        lines: list[str] = [Boundary.open(BoundaryType.AVAILABLE_TOOLS)]
        for tool in tools.values():
            lines.append(f"  {Boundary.open(BoundaryType.TOOL)}")
            lines.append(f"    {Boundary.open(BoundaryType.NAME)}{tool.name}{Boundary.close(BoundaryType.NAME)}")
            lines.append(
                f"    {Boundary.open(BoundaryType.DESCRIPTION)}{tool.description}{Boundary.close(BoundaryType.DESCRIPTION)}"
            )
            lines.append(f"  {Boundary.close(BoundaryType.TOOL)}")
        lines.append(Boundary.close(BoundaryType.AVAILABLE_TOOLS))

        return "\n".join(lines)
