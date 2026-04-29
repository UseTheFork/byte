from typing import override

from byte.tools import BaseTool, ToolResult
from byte.web import ChromiumService


class SearchWebTool(BaseTool):
    name: str = "search_web"
    description: str = (
        "Searches the web for information matching the given query and returns relevant page content as markdown."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string used to find relevant web pages.",
            },
            "max_results": {
                "type": "integer",
                "description": "The maximum number of search results to return. Defaults to 5 if not specified.",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    @override
    async def run(
        self,
        query: str = "",
        **kwargs,
    ) -> ToolResult:

        chromium_service = self.app.make(ChromiumService)
        markdown_content = await chromium_service.do_search(query)

        self.app["log"].info(markdown_content)

        return ToolResult(result={"content": markdown_content})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
