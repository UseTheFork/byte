from typing import List, Type

from byte import Command, Service, ServiceProvider
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
from byte.node import BaseAgentNode
from byte.tools import BaseTool
from byte.workflow import BaseWorkflow


class ConstitutionServiceProvider(ServiceProvider):
    """Service provider for the constitution domain.

    Registers and boots the ConstitutionService, which loads the project
    constitution from ``.byte/constitution.json`` on startup.
    """

    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            ConstitutionAgentNode,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            ConstitutionCommand,
            InitializeCommand,
            # keep-sorted end
        ]

    def workflows(self) -> List[Type[BaseWorkflow]]:
        return [
            # keep-sorted start
            ConstitutionWorkflow,
            # keep-sorted end
        ]

    def tools(self) -> List[Type[BaseTool]]:
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

    def services(self) -> List[Type[Service]]:
        return [
            ConstitutionService,
        ]

    async def boot(self) -> None:
        """Boot the constitution service."""
        self.app.make(ConstitutionService)
