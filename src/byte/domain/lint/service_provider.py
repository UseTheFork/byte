from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.cli import Command
from byte.domain.lint import LintCommand, LintService


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
