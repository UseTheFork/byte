from abc import ABC, abstractmethod

from byte.container import Container


class ServiceProvider(ABC):
    """Base service provider class that all providers should extend."""

    def __init__(self):
        self.container = None

    def set_container(self, container: Container):
        """Set the container instance."""
        self.container = container

    @abstractmethod
    def register(self, container: Container):
        """Register services in the container."""
        pass

    def boot(self, container: Container):
        """Boot services after all providers have been registered."""
        pass

    def provides(self) -> list:
        """Return list of services this provider provides."""
        return []
