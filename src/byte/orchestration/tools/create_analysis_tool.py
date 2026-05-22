from typing import List, override

from byte.tools import BaseTool, ToolResult


class CreateAnalysisTool(BaseTool):
    name: str = "record_analysis"
    description: str = (
        "Record a concise analysis of the subject matter before proceeding to the next phase. "
        "Use this to summarise key observations and reasoning, providing context for subsequent decisions. "
    )

    input_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A short, high-level summary of the subject matter being analysed.",
            },
            "observations": {
                "type": "array",
                "description": "A list of individual observations, one per logical point of note.",
                "items": {
                    "type": "string",
                    "description": "A single observation (e.g. 'Input validation was added to the registration handler').",
                },
            },
        },
        "required": [],
        "additionalProperties": False,
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        summary = result.result.get("summary", "")
        observations: list = result.result.get("observations", [])
        observations_text = "\n".join(f"- {observation}" for observation in observations)
        return f"Analysis recorded.\n\nSummary: {summary}\n\nObservations:\n{observations_text}"

    @override
    async def run(self, summary: str = "", observations: List[str] = [], **kwargs) -> ToolResult:
        return ToolResult(result={"summary": summary, "observations": observations})
