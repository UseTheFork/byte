from byte import ServiceProvider
from byte.coder import CoderAgentNode, CoderCommand, CoderWorkflow


class CoderServiceProvider(ServiceProvider):
    """"""

    def agents(self):
        return [
            # keep-sorted start
            CoderAgentNode,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            CoderCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            CoderWorkflow,
            # keep-sorted end
        ]
