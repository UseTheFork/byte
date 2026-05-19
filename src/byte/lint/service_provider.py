from byte import ServiceProvider
from byte.lint import LintCommand, LintService, LintTool


class LintServiceProvider(ServiceProvider):
    """Service provider for code linting functionality.

    Registers AI-integrated linting service that can analyze code quality
    and formatting issues. Integrates with the command registry and provides
    programmatic access for agent workflows.
    Usage: Register with container to enable `/lint` command and lint service
    """

    def tools(self):
        """Returns the list of git-related tools available to the agent."""
        return [
            # keep-sorted start
            LintTool
            # keep-sorted end
        ]

    def services(self):
        return [LintService]

    def commands(self):
        return [LintCommand]
