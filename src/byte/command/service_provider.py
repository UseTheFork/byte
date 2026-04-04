from byte import CommandRegistryService
from byte.support import ServiceProvider


class CommandServiceProvider(ServiceProvider):
    """Service provider for Command system."""

    def services(self):
        return [CommandRegistryService]
