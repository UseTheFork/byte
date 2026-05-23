from byte import ServiceProvider
from byte.specs import (
    CreateSpecPhaseWorkflow,
    CreateSpecWorkflow,
    CreateTaskTool,
    SpecCommand,
    SpecCreatorAgentNode,
    SpecTaskCommand,
    SpecTaskCreatorAgentNode,
)
from byte.specs.service.spec_loader_service import SpecLoaderService
from byte.specs.tools.create_spec_tool import CreateSpecTool
from byte.specs.tools.edit_task_tool import EditTaskTool


class SpecsServiceProvider(ServiceProvider):
    """Service provider for the specs domain.

    Registers services for spec loading and management. Specs are markdown
    files with YAML frontmatter stored under ``.byte/specs/``.

    Usage: Register with the application container to enable spec loading.
    """

    def agents(self):
        return [
            # keep-sorted start
            SpecCreatorAgentNode,
            SpecTaskCreatorAgentNode,
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            SpecLoaderService,
            # keep-sorted end
        ]

    def tools(self):
        return [
            # keep-sorted start
            CreateSpecTool,
            CreateTaskTool,
            EditTaskTool,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            SpecCommand,
            SpecTaskCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            CreateSpecWorkflow,
            CreateSpecPhaseWorkflow,
            # keep-sorted end
        ]

    async def boot(self) -> None:
        """Boot spec services."""
        spec_loader_service = self.app.make(SpecLoaderService)
        self.app.booted(spec_loader_service.reload)
