from byte.harness import (
    AgentHarnessWorkflow,
    BootstrapAgentTool,
    BootstrapSkillsFilesTool,
    BootstrapSkillsTool,
    HarnessAgentNode,
)
from byte.support import ServiceProvider


class HarnessServiceProvider(ServiceProvider):
    def agents(self):
        return [
            # keep-sorted start
            HarnessAgentNode,
            # keep-sorted end
        ]

    def tools(self):
        return [
            # keep-sorted start
            BootstrapAgentTool,
            BootstrapSkillsFilesTool,
            BootstrapSkillsTool,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            AgentHarnessWorkflow,
            # keep-sorted end
        ]
