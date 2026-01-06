"""Lint domain for code linting and formatting operations."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.lint.command.lint_command import LintCommand
    from byte.lint.exceptions import LintConfigException
    from byte.lint.service.lint_service import LintService
    from byte.lint.service_provider import LintServiceProvider
    from byte.lint.types import LintCommandType, LintFile

__all__ = (
    "LintCommand",
    "LintCommandType",
    "LintConfigException",
    "LintFile",
    "LintService",
    "LintServiceProvider",
)

_dynamic_imports = {
    "LintServiceProvider": "service_provider",
    "LintCommand": "command.lint_command",
    "LintCommandType": "types",
    "LintConfigException": "exceptions",
    "LintFile": "types",
    "LintService": "service.lint_service",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
