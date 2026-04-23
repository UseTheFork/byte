from abc import ABCMeta
from typing import Any

from langchain_core.tools.base import BaseTool as LangchainBaseTool


class BaseTool(LangchainBaseTool, metaclass=ABCMeta):
    extras: dict[str, Any] | None = {"eager_input_streaming": True}

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass
