"""Subgraph domain for AI agent subgraph implementations."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.subgraph.implementations.ask_agent import AskAgent
    from byte.subgraph.implementations.base_agent import BaseAgent
    from byte.subgraph.implementations.coder_agent import CoderAgent
    from byte.subgraph.implementations.commit_agent import CommitAgent

__all__ = (
    "AskAgent",
    "BaseAgent",
    "CoderAgent",
    "CommitAgent",
)

_dynamic_imports = {
    # keep-sorted start
    "AskAgent": "implementations.ask_agent",
    "BaseAgent": "implementations.base_agent",
    "CoderAgent": "implementations.coder_agent",
    "CommitAgent": "implementations.commit_agent",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
