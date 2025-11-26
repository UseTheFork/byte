from byte.core.service_provider import ServiceProvider


class ToolsServiceProvider(ServiceProvider):
    """Service provider for agent tools and utilities.

    Registers reusable tools that can be shared across different agents,
    including file operations, git utilities, and system commands. Promotes
    code reuse and consistent tool behavior across the agent ecosystem.
    Usage: Automatically registered during bootstrap to make tools available
    """

    pass
