from byte import ServiceProvider
from byte.skills import (
    CreateSkillTool,
    CreateSkillWorkflow,
    LoadSkillTool,
    SkillCommand,
    SkillCreatorAgentNode,
    SkillLoaderService,
    SkillSelectAgentNode,
)


class SkillsServiceProvider(ServiceProvider):
    """Service provider for the skills domain.

    Registers services for skill loading, tracking, and management.
    Enables the agent system to discover, load, and track which skills
    have been activated during a session.
    Usage: Register with container to enable skill tracking
    """

    def agents(self):
        return [
            # keep-sorted start
            SkillCreatorAgentNode,
            SkillSelectAgentNode,
            # keep-sorted end
        ]

    def tools(self):
        return [
            # keep-sorted start
            CreateSkillTool,
            LoadSkillTool,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            SkillCommand,
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            SkillLoaderService,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            CreateSkillWorkflow,
            # keep-sorted end
        ]

    async def boot(self):
        """Boot skill services."""

        skill_loader_service = self.app.make(SkillLoaderService)
        self.app.booted(skill_loader_service.reload)
