from byte.harness import AgentHarnessWorkflow, BootstrapAgentTool, ExecutorAgentNode, HarnessAgentNode
from byte.support import ServiceProvider


class HarnessServiceProvider(ServiceProvider):
    def agents(self):
        return [
            # keep-sorted start
            ExecutorAgentNode,
            HarnessAgentNode,
            # keep-sorted end
        ]

    def tools(self):
        return [
            # keep-sorted start
            BootstrapAgentTool,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            AgentHarnessWorkflow,
            # keep-sorted end
        ]
