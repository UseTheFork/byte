"""Git domain for repository operations and version control integration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.git.command.commit_command import CommitCommand
    from byte.git.schemas import CommitGroup, CommitMessage, CommitPlan
    from byte.git.service.commit_service import CommitService
    from byte.git.service.git_service import GitService
    from byte.git.service_provider import GitServiceProvider

__all__ = (
    "CommitCommand",
    "CommitGroup",
    "CommitMessage",
    "CommitPlan",
    "CommitService",
    "GitService",
    "GitServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "CommitCommand": "command.commit_command",
    "CommitGroup": "schemas",
    "CommitMessage": "schemas",
    "CommitPlan": "schemas",
    "CommitService": "service.commit_service",
    "GitService": "service.git_service",
    "GitServiceProvider": "service_provider",
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
