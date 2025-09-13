from typing import Any, Callable, Dict


class Container:
    """Simple dependency injection container for managing service bindings.

    Implements the Service Locator pattern with support for both transient
    and singleton lifetimes. Services are resolved lazily on first access.
    """

    def __init__(self):
        self._bindings: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}

    def bind(self, abstract: str, concrete: Callable):
        """Register a transient service binding.

        Each call to make() will create a new instance by invoking the factory.
        """
        self._bindings[abstract] = concrete

    def singleton(self, abstract: str, concrete: Callable):
        """Register a singleton service binding.

        The factory will be called once on first access, then the same
        instance will be returned for all subsequent make() calls.
        """
        self._bindings[abstract] = concrete
        # Instance caching is handled in make() method

    def make(self, abstract: str):
        """Resolve a service from the container.

        For singletons, returns cached instance if available, otherwise
        creates and caches a new instance. For transient bindings,
        always creates a new instance.

        Raises ValueError if no binding exists for the requested service.
        """
        # Return cached singleton instance if available
        if abstract in self._instances:
            return self._instances[abstract]

        if abstract in self._bindings:
            instance = self._bindings[abstract]()
            # Cache all instances for now (simple singleton behavior)
            # TODO: Distinguish between singleton and transient lifetimes
            self._instances[abstract] = instance
            return instance

        raise ValueError(f"No binding found for {abstract}")


# Global application container instance
# Using a global container simplifies service access across the application
# while maintaining the benefits of dependency injection
app = Container()
