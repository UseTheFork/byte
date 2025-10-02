from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.lint.command.lint_command import LintCommand
from byte.domain.lint.service.lint_service import LintService


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    def services(self) -> List[Type[Service]]:
        return [LintService]

    def commands(self) -> List[Type[Command]]:
        return [LintCommand]
