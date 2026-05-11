from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from byte.support.mixins.bootable import Bootable
from byte.tools.exceptions import ToolException, ToolRunException, ToolValidationException
from byte.tools.schemas import ToolResult

if TYPE_CHECKING:
    from byte.orchestration import BaseState


class BaseTool(ABC, Bootable):
    # args_schema: dict[str, Any] | None = {"eager_input_streaming": True}
    # extras: dict[str, Any] | None = {"eager_input_streaming": True}

    name: str
    description: str
    input_schema: dict[str, Any]
    harness_invocable: bool = True
    terminates_turn: bool = False

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> ToolResult:
        pass

    async def invoke(
        self,
        args: dict,
        state: BaseState,
        tool_call_id: str,
    ) -> ToolResult:

        self.tool_call_id = tool_call_id

        required = self.input_schema.get("required", [])
        missing = [field for field in required if field not in args]
        if missing:
            raise ToolValidationException(f"Missing required argument(s): {', '.join(missing)}")

        try:
            return await self.run(**args, state=state)
        except ToolException:
            self.app["log"].exception("Oops")
            raise
        except Exception as e:
            self.app["log"].exception("Oops")
            raise ToolRunException(str(e)) from e

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        return {
            "name": cls.name,
            "description": cls.description,
            "input_schema": cls.input_schema,
        }

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        """Format the tool result for display in the TUI.

        Override this method to customize how a tool's result is presented.
        """
        return cls.format_tool_message(result)

    @classmethod
    @abstractmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        """Format the tool result as a tool message returned to the LLM.

        Override this method to customize the message content sent back to the model.
        By default returns the raw result string.
        """
        ...
