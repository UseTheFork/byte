"""LLM domain for language model integration and AI operations."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.llm.schemas import (
        AnthropicSchema,
        GoogleSchema,
        LLMSchema,
        ModelBehavior,
        ModelConstraints,
        ModelParams,
        ModelSchema,
        OpenAiSchema,
        ReinforcementMode,
    )
    from byte.llm.service.llm_service import LLMService
    from byte.llm.service_provider import LLMServiceProvider

__all__ = (
    "AnthropicSchema",
    "GoogleSchema",
    "LLMSchema",
    "LLMService",
    "LLMServiceProvider",
    "ModelBehavior",
    "ModelConstraints",
    "ModelParams",
    "ModelSchema",
    "OpenAiSchema",
    "ReinforcementMode",
)

_dynamic_imports = {
    "AnthropicSchema": "schemas",
    "GoogleSchema": "schemas",
    "LLMSchema": "schemas",
    "LLMService": "service.llm_service",
    "LLMServiceProvider": "service_provider",
    "ModelBehavior": "schemas",
    "ModelConstraints": "schemas",
    "ModelParams": "schemas",
    "ModelSchema": "schemas",
    "OpenAiSchema": "schemas",
    "ReinforcementMode": "schemas",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
