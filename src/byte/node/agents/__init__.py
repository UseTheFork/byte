from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.node.agents.ask_agent_node import AskAgentNode
    from byte.node.agents.coder_agent_node import CoderAgentNode
    from byte.node.agents.commit_agent_node import CommitAgentNode
    from byte.node.agents.constitution_agent_node import ConstitutionAgentNode
    from byte.node.agents.executor_agent_node import ExecutorAgentNode
    from byte.node.agents.harness_agent_node import HarnessAgentNode
    from byte.node.agents.skill_creator_agent_node import SkillCreatorAgentNode

__all__ = (
    "AskAgentNode",
    "CoderAgentNode",
    "CommitAgentNode",
    "ConstitutionAgentNode",
    "ExecutorAgentNode",
    "HarnessAgentNode",
    "SkillCreatorAgentNode",
)

_dynamic_imports = {
    # keep-sorted start
    "AskAgentNode": "ask_agent_node",
    "CoderAgentNode": "coder_agent_node",
    "CommitAgentNode": "commit_agent_node",
    "ExecutorAgentNode": "executor_agent_node",
    "HarnessAgentNode": "harness_agent_node",
    "SkillCreatorAgentNode": "skill_creator_agent_node",
    "ConstitutionAgentNode": "constitution_agent_node",
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
