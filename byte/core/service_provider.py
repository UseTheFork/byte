from abc import ABC, abstractmethod

from byte.container import Container


class ServiceProvider(ABC):
    """Base service provider class that all providers should extend.
    
    Implements the Service Provider pattern to organize dependency registration
    and initialization. Each provider encapsulates the setup logic for a specific
    domain or cross-cutting concern, promoting modular architecture.
    """

    def __init__(self):
        # Optional container reference for providers that need it during initialization
        self.container = None

    def set_container(self, container: Container):
        """Set the container instance for providers that need container access.
        
        Allows providers to store a reference for complex initialization scenarios
        where the container is needed beyond the register/boot phases.
        """
        self.container = container

    @abstractmethod
    def register(self, container: Container):
        """Register services in the container without initializing them.
        
        This is phase 1 of the two-phase initialization. Only bind service
        factories to the container - don't create instances or configure
        dependencies yet, as other providers may not be registered.
        """
        pass

    def boot(self, container: Container):
        """Boot services after all providers have been registered.
        
        This is phase 2 where services can safely reference each other since
        all bindings are now available. Use this phase for:
        - Registering event listeners
        - Configuring service relationships  
        - Performing initialization that requires other services
        """
        pass

    def provides(self) -> list:
        """Return list of service identifiers this provider makes available.
        
        Used for documentation and potential dependency resolution validation.
        Should match the keys used in register() method calls.
        """
        return []
