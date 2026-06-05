from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Type, TypeVar, Union, overload

from byte.support import Str
from byte.support.mixins import Bootable
from byte.tui import Console

T = TypeVar("T")


if TYPE_CHECKING:
    from byte import Application, LogService
    from byte.config import ByteConfig, Repository


class Container:
    """Manage service bindings and dependency resolution."""

    _instance = None

    def __init__(self):
        """Initialize the container with empty service registries."""
        self._singletons = {}
        self._transients = {}
        self._instances = {}

        self._service_providers = []

    @classmethod
    def set_instance(cls, container):
        """Set the globally available instance of the container."""
        cls._instance = container
        return container

    @classmethod
    def get_instance(cls):
        """Get the globally available instance of the container."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _normalize_abstract(self, abstract) -> str:
        """Normalize abstract type to string representation."""
        return Str.class_to_string(abstract)

    def bind(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a transient service binding."""
        if concrete is None:

            def concrete():
                return service_class(app=self)

        service_class_str = self._normalize_abstract(service_class)

        self._transients[service_class_str] = concrete

    def singleton(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a singleton service binding."""
        service_class_str = self._normalize_abstract(service_class)

        if concrete is None:
            # Auto-create factory for class
            def concrete():
                return service_class(app=self)

        self._singletons[service_class_str] = concrete

    def _create_instance(self, factory: Callable, **kwargs) -> Any:
        """Create and boot an instance from the given factory."""
        instance = factory()

        # TODO: Centralize this.
        if isinstance(instance, Bootable):
            instance.ensure_booted(**kwargs)

        return instance

    @overload
    def make(self, abstract: Type[T], **kwargs) -> T: ...

    @overload
    def make(self, abstract: str, **kwargs) -> Any: ...

    def make(self, abstract: Union[Type[T], str], **kwargs) -> Union[T, Any]:
        """Resolve a service from the container."""

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
        """Build an instance of the given type with container injection."""
        # Pass self as app= along with any other kwargs
        instance = abstract(app=self, **kwargs)

        if isinstance(instance, Bootable):
            instance.ensure_booted(**kwargs)

        return instance

    def flush(self) -> None:
        """Clear all bindings and instances from the container."""
        self._singletons.clear()
        self._transients.clear()
        self._instances.clear()
        self._service_providers.clear()

    def instance(self, abstract, instance: T) -> T:
        """Register an existing instance as shared in the container."""
        abstract_str = self._normalize_abstract(abstract)

        # Store the instance
        self._instances[abstract_str] = instance

        return instance

    def bound(self, abstract) -> bool:
        """Determine if the given abstract type has been bound."""
        abstract_str = self._normalize_abstract(abstract)
        return abstract_str in self._instances

    # TODO: Can the below overloads be moved in to application?
    @overload
    def __getitem__(self, abstract: Literal["args"], **kwargs) -> Repository: ...

    @overload
    def __getitem__(self, abstract: Literal["env"], **kwargs) -> str: ...

    @overload
    def __getitem__(self, abstract: Literal["console"], **kwargs) -> Console: ...

    @overload
    def __getitem__(self, abstract: Literal["config"], **kwargs) -> ByteConfig: ...

    @overload
    def __getitem__(self, abstract: Literal["version"], **kwargs) -> str: ...

    @overload
    def __getitem__(self, abstract: Literal["log"], **kwargs) -> LogService: ...

    @overload
    def __getitem__(self, abstract: Literal["app"], **kwargs) -> Application: ...

    @overload
    def __getitem__(self, abstract: Literal["path"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.app"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.root"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.config"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.cache"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.conventions"], **kwargs) -> Path: ...

    @overload
    def __getitem__(self, abstract: Literal["path.session_context"], **kwargs) -> Path: ...

    def __getitem__(self, key: str) -> Any:
        """Resolve an item from the container by key."""
        return self.make(key)

    def __setitem__(self, key, value: Any) -> None:
        """Register a binding or instance with the container."""
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
