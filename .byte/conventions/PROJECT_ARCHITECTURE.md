# Project Architecture Convention

## Key Principles

- **Domain-Driven Design**: Features organized by domain (files, git, agent) with clear boundaries
- **Dependency Injection**: Container-based DI with two-phase initialization (register → boot)
- **Service Provider Pattern**: Each domain has a ServiceProvider that encapsulates registration
- **Mixin Composition**: Services compose behavior (Bootable, Injectable, Eventable, Configurable)

## Directory Structure

```
src/byte/
├── core/                    # Framework primitives (Container, EventBus)
│   ├── service/            # Base service classes
│   └── mixins/             # Reusable behavior mixins
└── domain/{domain}/         # Feature domains
    ├── config.py           # Domain configuration schema
    ├── service_provider.py # Registration & boot logic
    ├── service/            # Business logic services
    ├── command/            # User-facing commands
    └── agent/              # AI agent implementations
```

## Service Provider Pattern

```python
class FileServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [FileService, FileDiscoveryService]  # Auto-registered as singletons

    def commands(self) -> List[Type[Command]]:
        return [AddFileCommand, DropFileCommand]  # Auto-registered & booted

    async def boot(self, container: Container):
        # Phase 2: Wire dependencies, register event listeners
        event_bus = await container.make(EventBus)
        event_bus.on(EventType.PRE_PROMPT, self.hook_method)
```

Bootstrap order in `bootstrap.py` matters: core services first, domain services after.

## Base Classes

- **Service**: `ABC + Bootable + Injectable + Eventable + Configurable` - business logic
- **Agent**: `ABC + Bootable + Injectable + Eventable + Configurable` - AI workflows
- **Node**: `ABC + Bootable + Configurable + Eventable` - LangGraph nodes
- **Command**: `ABC + Bootable + Injectable + Configurable + UserInteractive` - user commands

All implement `async def boot()` for initialization requiring container access.

## Dependency Resolution

- Register: `app.singleton(Service)` or `app.bind(Service)` for transient
- Resolve: `service = await self.make(ServiceClass)` from any Bootable/Injectable
- Auto-boot: Services implementing Bootable are booted on first `make()`
- Lazy: Services instantiated only when first requested

## Event-Driven Communication

```python
# Register listener in ServiceProvider.boot()
event_bus.on(EventType.FILE_ADDED, self.handle_file_added)

# Emit from Eventable services
await self.emit(Payload(event_type=EventType.FILE_ADDED, data={...}))
```

Decouples domains, allows multiple listeners, enables hooks without tight coupling.

## Things to Avoid

- ❌ Direct instantiation (`FileService()`) → use `await self.make(ServiceClass)`
- ❌ Global state outside Container → register as singleton
- ❌ Synchronous `__init__` for I/O → use `async def boot()`
- ❌ Cross-domain concrete imports → depend on abstractions or use events
