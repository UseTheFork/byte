from byte import ServiceProvider
from byte.documentation import DocumentationAgentNode, DocumentationCommand, DocumentationWorkflow


class DocumentationServiceProvider(ServiceProvider):
    """Register documentation domain agents, commands, and workflows."""

    def agents(self):
        return [
            # keep-sorted start
            DocumentationAgentNode,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            DocumentationCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            DocumentationWorkflow,
            # keep-sorted end
        ]
