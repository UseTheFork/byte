from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.node.agents.ask_agent_node import AskAgentMessage, AskAgentNode
    from byte.node.agents.coder_agent_node import CoderAgentMessage, CoderAgentNode
    from byte.node.agents.coder_plan_agent_node import CoderPlanAgentMessage, CoderPlanAgentNode
    from byte.node.agents.commit_agent_node import CommitAgentMessage, CommitAgentNode

__all__ = (
    "AskAgentMessage",
    "AskAgentNode",
    "CoderAgentMessage",
    "CoderAgentNode",
    "CoderPlanAgentMessage",
    "CoderPlanAgentNode",
    "CommitAgentMessage",
    "CommitAgentNode",
)

_dynamic_imports = {
    # keep-sorted start
    "AskAgentMessage": "ask_agent_node",
    "AskAgentNode": "ask_agent_node",
    "CoderAgentMessage": "coder_agent_node",
    "CoderAgentNode": "coder_agent_node",
    "CoderPlanAgentMessage": "coder_plan_agent_node",
    "CoderPlanAgentNode": "coder_plan_agent_node",
    "CommitAgentMessage": "commit_agent_node",
    "CommitAgentNode": "commit_agent_node",
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
