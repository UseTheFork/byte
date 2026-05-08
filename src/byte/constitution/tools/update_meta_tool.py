from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class UpdateMetaTool(BaseTool):
    name: str = "constitution_update_meta"
    description: str = (
        "Update the constitution metadata: ratification date, last amended date, and/or version. "
        "Provide only the fields you want to change."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "ratification_date": {
                "type": "string",
                "description": "The original ratification date (ISO 8601, e.g. '2024-01-15'). "
                "Only provide if you want to change RATIFICATION_DATE.",
            },
            "last_amended_date": {
                "type": "string",
                "description": "The date the constitution was last amended (ISO 8601, e.g. '2026-05-08'). "
                "Only provide if you want to change LAST_AMENDED_DATE.",
            },
            "version": {
                "type": "string",
                "description": "The constitution version string (e.g. '1.2.0'). "
                "Only provide if you want to change CONSTITUTION_VERSION.",
            },
        },
        "required": [],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(
        self,
        ratification_date: str | None = None,
        last_amended_date: str | None = None,
        version: str | None = None,
        **kwargs,
    ) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            meta = service.update_meta(
                ratification_date=ratification_date,
                last_amended_date=last_amended_date,
                version=version,
            )
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        parts = []
        if ratification_date is not None:
            parts.append(f"ratification_date='{meta.ratified}'")
        if last_amended_date is not None:
            parts.append(f"last_amended_date='{meta.last_amended}'")
        if version is not None:
            parts.append(f"version='{meta.version}'")

        summary = ", ".join(parts) if parts else "no fields changed"
        return ToolResult(result={"message": f"Updated constitution metadata: {summary}."})
