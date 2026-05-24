from byte import ServiceProvider
from byte.research import ResearchAgentNode, ResearchCommand, ResearchWorkflow


class ResearchServiceProvider(ServiceProvider):
    """"""

    def agents(self):
        return [
            # keep-sorted start
            ResearchAgentNode,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            ResearchCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            ResearchWorkflow,
            # keep-sorted end
        ]
