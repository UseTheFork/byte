from byte import ServiceProvider
from byte.specs import CreateSpecWorkflow, SpecCommand
from byte.specs.service.spec_loader_service import SpecLoaderService
from byte.specs.tools.create_spec_tool import CreateSpecTool


class SpecsServiceProvider(ServiceProvider):
    """Service provider for the specs domain.

    Registers services for spec loading and management. Specs are markdown
    files with YAML frontmatter stored under ``.byte/specs/``.

    Usage: Register with the application container to enable spec loading.
    """

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
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            SpecCommand,
            # keep-sorted end
        ]

    def workflows(self):
        return [
            # keep-sorted start
            CreateSpecWorkflow,
            # keep-sorted end
        ]

    async def boot(self) -> None:
        """Boot spec services."""
        spec_loader_service = self.app.make(SpecLoaderService)
        self.app.booted(spec_loader_service.reload)
