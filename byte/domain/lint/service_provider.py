from typing import TYPE_CHECKING

from rich.console import Console

from byte.core.service_provider import ServiceProvider
from byte.domain.lint.commands import LintCommand
from byte.domain.lint.config import LintConfig
from byte.domain.lint.service import LintService

if TYPE_CHECKING:
    from byte.container import Container
    from byte.core.config.service import ConfigService


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    async def register(self, container: "Container") -> None:
        """Register lint services in the container.

        Usage: `provider.register(container)` -> binds lint service and command
        """
        # Register lint service and command
        container.bind("lint_service", lambda: LintService(container))
        container.bind("lint_command", lambda: LintCommand(container))

    async def configure(self, container: "Container") -> None:
        """Configure lint domain settings after registration but before boot.

        Handles lint-specific configuration parsing, validation, and storage.
        Usage: Called automatically during container configure phase
        """
        # Get the config service to access raw configuration data
        config_service: ConfigService = await container.make("config")

        # Get raw config data from all sources
        yaml_config, env_config, cli_config = config_service.get_raw_config()

        # Handle boolean conversion for enabled field from flat config
        enabled = yaml_config.get("lint", True)
        if isinstance(enabled, str):
            enabled = enabled.lower() == "true"

        # Handle lint-commands field from flat config
        commands = yaml_config.get("lint-commands")

        # Parse and validate lint configuration using the domain's config class
        lint_config = LintConfig(enabled=enabled, commands=commands)

        lint_service: LintService = await container.make("lint_service")
        lint_service.set_config(lint_config)

        if enabled:
            console: Console = await container.make("console")
            console.print("│", style="text")
            console.print("├─ Linting: [success]Enabled[/success]")

    async def boot(self, container: "Container") -> None:
        """Boot lint services and register commands with registry.

        Usage: `provider.boot(container)` -> `/lint` becomes available to users
        """
        command_registry = await container.make("command_registry")

        # Register lint command for user access
        await command_registry.register_slash_command(
            await container.make("lint_command")
        )

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["lint_service", "lint_command"]
