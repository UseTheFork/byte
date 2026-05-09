from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.node import BaseAgentNode
from byte.skills import (
    CreateSkillTool,
    CreateSkillWorkflow,
    LoadSkillTool,
    SkillCommand,
    SkillCreatorAgentNode,
    SkillLoaderService,
)
from byte.tools import BaseTool
from byte.workflow import BaseWorkflow


class SkillsServiceProvider(ServiceProvider):
    """Service provider for the skills domain.

    Registers services for skill loading, tracking, and management.
    Enables the agent system to discover, load, and track which skills
    have been activated during a session.
    Usage: Register with container to enable skill tracking
    """

    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            SkillCreatorAgentNode,
            # keep-sorted end
        ]

    def tools(self) -> List[Type[BaseTool]]:
        return [
            # keep-sorted start
            CreateSkillTool,
            LoadSkillTool,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            SkillCommand,
            # keep-sorted end
        ]

    def services(self) -> List[Type[Service]]:
        return [SkillLoaderService]

    def workflows(self) -> List[Type[BaseWorkflow]]:
        return [
            # keep-sorted start
            CreateSkillWorkflow,
            # keep-sorted end
        ]

    async def boot(self):
        """Boot skill services."""

        skill_loader_service = self.app.make(SkillLoaderService)
        self.app.booted(skill_loader_service.reload)
