from typing import List, Type

from langchain.tools import BaseTool

from byte import Command, Service, ServiceProvider
from byte.skills import CreateSkillTool, LoadSkillTool, SkillCommand, SkillLoaderService, SkillTrackerService


class SkillsServiceProvider(ServiceProvider):
    """Service provider for the skills domain.

    Registers services for skill loading, tracking, and management.
    Enables the agent system to discover, load, and track which skills
    have been activated during a session.
    Usage: Register with container to enable skill tracking
    """

    def tools(self) -> List[Type[BaseTool]]:
        return [
            CreateSkillTool,
            LoadSkillTool,
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            SkillCommand,
        ]

    def services(self) -> List[Type[Service]]:
        return [SkillLoaderService, SkillTrackerService]

    async def boot(self):
        """Boot skill services."""

        skill_loader_service = self.app.make(SkillLoaderService)
        self.app.booted(skill_loader_service.reload)
