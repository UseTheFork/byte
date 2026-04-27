from typing import Annotated, Any, Optional, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte import Application
from byte.tools import BaseTool, ToolResult
from byte.web import ChromiumService


class SearchWebToolInput(BaseModel):
    """Input for SearchWebTool"""

    query: str = Field(description="The search query string used to find relevant web pages.")
    max_results: Optional[int] = Field(
        default=5, description="The maximum number of search results to return. Defaults to 5 if not specified."
    )
    app: Annotated[Any | None, InjectedToolArg]


class SearchWebTool(BaseTool):
    name: str = "SearchWebTool"
    description: str = (
        "Searches the web for information matching the given query and returns relevant page content as markdown."
    )
    args_schema: ArgsSchema = SearchWebToolInput

    @override
    async def _arun(
        self,
        app: Application,
        query: str = "",
    ) -> ToolResult:

        chromium_service = app.make(ChromiumService)
        markdown_content = await chromium_service.do_search(query)

        app["log"].info(markdown_content)

        return ToolResult(result=markdown_content)
