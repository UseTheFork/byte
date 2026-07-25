from byte import ServiceProvider
from byte.lint.command.lint_command import LintCommand
from byte.lint.service.lint_service import LintService
from byte.lint.tools.lint_tool import LintTool


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    def tools(self):
        return [
            # keep-sorted start
            LintTool
            # keep-sorted end
        ]

    def services(self):
        return [
            # keep-sorted start
            LintService
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            LintCommand
            # keep-sorted end
        ]
