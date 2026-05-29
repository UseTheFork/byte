from typing import override

from byte.orchestration import BaseState
from byte.skills import SkillLoaderService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class BootstrapSkillsTool(BaseTool):
    name: str = "bootstrap_skills_tool"
    description: str = "Load skills into the agent harness based on the workflow requirements."
    input_schema = {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skill names to load into the harness.",
            },
        },
    }

    @override
    async def run(
        self,
        state: BaseState,
        skills: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        harness = state.get("harness", {})

        skill_loader_service = self.app.make(SkillLoaderService)

        invalid = [name for name in skills if skill_loader_service.get_skill(name) is None]
        if invalid:
            raise ToolValidationException(f"Unknown skill(s): {', '.join(invalid)}.")

        harness["skills"] = skills

        return ToolResult(
            result={"content": "OK"},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
