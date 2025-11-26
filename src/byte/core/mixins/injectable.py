from typing import TYPE_CHECKING, Optional, Type, TypeVar

if TYPE_CHECKING:
    from byte.container import Container

T = TypeVar("T")


class Injectable:
    """Mixin that provides direct access to container.make() without context.

    Enables services to resolve dependencies directly through their container
    reference instead of using the global context. Useful for services that
    need to resolve dependencies in non-async contexts or prefer explicit
    dependency resolution.
    Usage: `class MyService(Injectable): dependency = await self.make(SomeService)`
    """

    container: Optional["Container"]

    async def make(self, service_class: Type[T]) -> T:
        """Resolve a service from the container.

        Usage: `service = await self.make(ServiceClass)`
        """
        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")
        return await self.container.make(service_class)
