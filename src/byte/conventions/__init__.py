"""Knowledge domain commands for context management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.conventions.service.convention_context_service import ConventionContextService
    from byte.conventions.tools import load_conventions


__all__ = (
    "ConventionContextService",
    "ConventionsServiceProvider",
    "load_conventions",
)

_dynamic_imports = {
    # keep-sorted start
    "ConventionContextService": "service.convention_context_service",
    "ConventionsServiceProvider": "service_provider",
    "load_conventions": "tools",
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
