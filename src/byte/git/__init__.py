"""Git domain for repository operations and version control integration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.git.agents.commit_agent_node import CommitAgentNode
    from byte.git.command.commit_command import CommitCommand
    from byte.git.schemas import CommitMessage
    from byte.git.service.commit_service import CommitService
    from byte.git.service.git_service import GitService
    from byte.git.service_provider import GitServiceProvider
    from byte.git.tools.git_commit_tool import GitCommitTool
    from byte.git.tools.git_grep_tool import GitGrepTool
    from byte.git.tools.git_log_tool import GitLogTool
    from byte.git.workflows.commit_workflow import CommitWorkflow

__all__ = (
    "CommitAgentNode",
    "CommitCommand",
    "CommitMessage",
    "CommitService",
    "CommitWorkflow",
    "GitCommitTool",
    "GitGrepTool",
    "GitLogTool",
    "GitService",
    "GitServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "CommitAgentNode": "agents.commit_agent_node",
    "CommitCommand": "command.commit_command",
    "CommitMessage": "schemas",
    "CommitService": "service.commit_service",
    "CommitWorkflow": "workflows.commit_workflow",
    "GitCommitTool": "tools.git_commit_tool",
    "GitGrepTool": "tools.git_grep_tool",
    "GitLogTool": "tools.git_log_tool",
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
