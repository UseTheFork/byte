from typing import cast, override

from byte.orchestration import BaseState
from byte.orchestration.state import HarnessState
from byte.skills import SkillLoaderService
from byte.tools import BaseTool, ToolRegistryService, ToolResult


class BootstrapAgentTool(BaseTool):
    name: str = "bootstrap_agent"
    description: str = "Select skills, tools, and the prompt to add to the agent harness by name."
    input_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt to set for the harness.",
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skill names to add to the harness.",
            },
            "tools": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tools names to add to the harness.",
            },
        },
        "required": [],
    }

    @override
    async def run(
        self,
        prompt: str,
        skills: list[str],
        tools: list[str],
        state: BaseState,
        **kwargs,
    ) -> ToolResult:
        harness = cast(HarnessState, state.get("harness", {}))
        harness["prompt"] = prompt

        tool_registry_service = self.app.make(ToolRegistryService)

        invalid = [name for name in tools if not tool_registry_service.has_tool(name)]
        if invalid:
            return ToolResult(result={"content": f"Unknown tool(s): {', '.join(invalid)}. No changes made."})

        harness = cast(HarnessState, state.get("harness", {}))
        harness["tools"] = tools

        skill_loader_service = self.app.make(SkillLoaderService)

        invalid = [name for name in skills if skill_loader_service.get_skill(name) is None]
        if invalid:
            return ToolResult(result={"content": f"Unknown skill(s): {', '.join(invalid)}. No changes made."})

        harness = cast(HarnessState, state.get("harness", {}))
        harness["skills"] = skills

        return ToolResult(
            result={"content": f"Harness skills set to: {', '.join(skills)}."},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
