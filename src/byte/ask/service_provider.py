from byte import ServiceProvider
from byte.ask import AskAgentNode, AskCommand, AskWorkflow


class AskServiceProvider(ServiceProvider):
    """"""

    def agents(self):
        return [
            # keep-sorted start
            AskAgentNode,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            AskCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            AskWorkflow,
            # keep-sorted end
        ]
