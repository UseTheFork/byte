"""Harness domain — bootstrapping utilities for agents."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.harness.service_provider import HarnessServiceProvider
    from byte.harness.tools.bootstrap_agent_tool import BootstrapAgentTool


__all__ = ("BootstrapAgentTool", "HarnessServiceProvider")

_dynamic_imports = {
    # keep-sorted start
    "BootstrapAgentTool": "tools.bootstrap_agent_tool",
    "HarnessServiceProvider": "service_provider",
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
