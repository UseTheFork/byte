from typing import List, Type

from byte.harness import AgentHarnessWorkflow, BootstrapAgentTool, ExecutorAgentNode, HarnessAgentNode
from byte.node import BaseAgentNode
from byte.support import ServiceProvider
from byte.tools import BaseTool
from byte.workflow import BaseWorkflow


class HarnessServiceProvider(ServiceProvider):
    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            HarnessAgentNode,
            ExecutorAgentNode,
            # keep-sorted end
        ]

    def tools(self) -> List[Type[BaseTool]]:
        return [
            # keep-sorted start
            BootstrapAgentTool,
            # keep-sorted end
        ]

    def workflows(self) -> List[Type[BaseWorkflow]]:
        return [
            # keep-sorted start
            AgentHarnessWorkflow,
            # keep-sorted end
        ]
