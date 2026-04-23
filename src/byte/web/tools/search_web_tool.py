from typing import Any, override

from git import TYPE_CHECKING
from langchain_core.tools import ArgsSchema

from byte.tools import BaseTool, ToolResult
from byte.web import ChromiumService

if TYPE_CHECKING:
    from byte import Application

search_web_schema = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "The search query string used to find relevant web pages."},
        "max_results": {
            "type": "int",
            "description": "The maximum number of search results to return. Defaults to 5 if not specified.",
            "default": 5,
        },
    },
    "required": ["query"],
}


class SearchWebTool(BaseTool):
    name: str = "SearchWebTool"
    description: str = (
        "Searches the web for information matching the given query and returns relevant page content as markdown."
    )
    args_schema: ArgsSchema | None = search_web_schema

    @override
    async def _arun(
        self,
        query: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        chromium_service = app.make(ChromiumService)
        markdown_content = await chromium_service.do_search(query)

        app["log"].info(markdown_content)

        return ToolResult(result=markdown_content)
