from byte import ServiceProvider
from byte.constitution import ConstitutionAgentNode, ConstitutionCommand, ConstitutionWorkflow, InitializeCommand
from byte.constitution.service.constitution_service import ConstitutionService
from byte.constitution.tools import (
    AddGovernanceRuleTool,
    AddPrincipleTool,
    AddSectionItemTool,
    AddSectionTool,
    DeleteGovernanceRuleTool,
    DeletePrincipleTool,
    DeleteSectionItemTool,
    DeleteSectionTool,
    UpdateMetaTool,
)


class ConstitutionServiceProvider(ServiceProvider):
    """Service provider for the constitution domain.

    Registers and boots the ConstitutionService, which loads the project
    constitution from ``.byte/constitution.json`` on startup.
    """

    def agents(self):
        return [
            # keep-sorted start
            ConstitutionAgentNode,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            ConstitutionCommand,
            InitializeCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            ConstitutionWorkflow,
            # keep-sorted end
        ]

    def tools(self):
        return [
            # keep-sorted start
            AddGovernanceRuleTool,
            AddPrincipleTool,
            AddSectionItemTool,
            AddSectionTool,
            DeleteGovernanceRuleTool,
            DeletePrincipleTool,
            DeleteSectionItemTool,
            DeleteSectionTool,
            UpdateMetaTool,
            # keep-sorted end
        ]

    def services(self):
        return [
            ConstitutionService,
        ]

    async def boot(self):
        """Boot the constitution service."""
        self.app.make(ConstitutionService)
