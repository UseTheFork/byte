import inspect
from typing import Any, Callable, Optional, Type, TypeVar

from byte.support.mixins import Bootable

T = TypeVar("T")


class Container:
    """Simple dependency injection container for managing service bindings.

    Implements the Service Locator pattern with support for both transient
    and singleton lifetimes. Services are resolved lazily on first access.
    """

    _instance = None

    def __init__(self):
        self._singletons = {}
        self._transients = {}
        self._instances = {}

        self._service_providers = []

    @classmethod
    def set_instance(cls, container):
        """
        Set the globally available instance of the container.

        Args:
            container: Container instance to set as singleton.

        Returns:
            The container instance.
        """
        cls._instance = container
        return container

    @classmethod
    def get_instance(cls):
        """
        Get the globally available instance of the container.

        Returns:
            Container instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _normalize_abstract(self, abstract) -> str:
        """
        Normalize abstract type to string representation.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            String representation of the abstract type.
        """
        if isinstance(abstract, type):
            return f"{abstract.__module__}.{abstract.__qualname__}"
        return abstract

    def bind(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a transient service binding.

        Usage:
        container.bind(FileService, lambda: FileService(container))
        container.bind(FileService)  # Auto-creates with container
        """
        if concrete is None:

            def concrete():
                return service_class(self)

        service_class_str = self._normalize_abstract(service_class)

        self._transients[service_class_str] = concrete

    def singleton(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a singleton service binding.

        Usage:
        container.singleton(FileService, lambda: FileService(container))
        container.singleton(FileService)  # Auto-creates with container
        """
        service_class_str = self._normalize_abstract(service_class)

        if concrete is None:
            # Auto-create factory for class
            def concrete():
                return service_class(self)

        self._singletons[service_class_str] = concrete

    def _create_instance(self, factory: Callable, **kwargs) -> Any:
        """Helper to create and boot instances."""
        instance = factory()

        # TODO: Centralize this.
        if isinstance(instance, Bootable):
            instance.ensure_booted(**kwargs)

        return instance

    def make(self, abstract, **kwargs) -> T:
        """Resolve a service from the container.

        Usage:
        file_service = await container.make(FileService)
        """

        abstract_str = self._normalize_abstract(abstract)

        # Return cached singleton instance if available
        if abstract_str in self._instances:
            return self._instances[abstract_str]

        # Try to create from singleton bindings
        if abstract_str in self._singletons:
            factory = self._singletons[abstract_str]
            instance = self._create_instance(factory, **kwargs)
            self._instances[abstract_str] = instance  # Cache it
            return instance

        # Try to create from transient bindings
        if abstract_str in self._transients:
            factory = self._transients[abstract_str]
            return self._create_instance(factory, **kwargs)  # Don't cache

        # Fallback to build if abstract is a type
        if isinstance(abstract, type):
            return self.build(abstract, **kwargs)

        raise ValueError(f"No binding found for {abstract_str}")

    def build(self, abstract: Type[T], **kwargs) -> T:
        """Build an instance of the given type with container injection.

        Usage: `instance = container.build(MyClass, extra_arg=value)`
        """
        # Pass self as app= along with any other kwargs
        instance = abstract(app=self, **kwargs)

        if isinstance(instance, Bootable):
            print(123)
            print(123)
            print(123)
            instance.ensure_booted(**kwargs)

        return instance

    def flush(self) -> None:
        """Reset the container state, clearing all bindings and instances.

        Usage: `container.reset()` -> clears all state for fresh start
        """
        self._singletons.clear()
        self._transients.clear()
        self._instances.clear()
        self._service_providers.clear()

    def instance(self, abstract, instance: T) -> T:
        """
        Register an existing instance as shared in the container.

        Args:
            abstract: Abstract type identifier.
            instance: The instance to register.

        Returns:
            The registered instance.
        """
        abstract_str = self._normalize_abstract(abstract)

        # Store the instance
        self._instances[abstract_str] = instance

        return instance

    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return abstract_str in self._instances

    def __getitem__(self, key: str) -> Any:
        """Resolve an item from the container by key."""
        return self.make(key)

    def __setitem__(self, key, value: Any) -> None:
        """Register a binding or instance with the container."""
        # If the value is a closure, we'll bind it as a factory.
        # Otherwise, we'll register it as a concrete instance.
        if callable(value) and not inspect.isclass(value):
            self.bind(key, value)
        else:
            self.instance(key, value)

    def __delitem__(self, key: str) -> None:
        """Remove a binding from the container."""
        key_str = self._normalize_abstract(key)
        if key_str in self._instances:
            del self._instances[key_str]
        if key_str in self._transients:
            del self._transients[key_str]

    def __contains__(self, key: str) -> bool:
        """Determine if a given type is bound in the container."""
        return self.bound(key)
