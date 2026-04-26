from abc import ABCMeta
from typing import Any

from langchain_core.tools.base import BaseTool as LangchainBaseTool


class BaseTool(LangchainBaseTool, metaclass=ABCMeta):
    extras: dict[str, Any] | None = {"eager_input_streaming": True}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate the tool class definition during subclass creation.

        Args:
            **kwargs: Additional keyword arguments passed to the parent class.

        Raises:
            SchemaAnnotationError: If `args_schema` has incorrect type annotation.
        """
        super().__init_subclass__(**kwargs)

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass
