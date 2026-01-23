# Directory Structure & Module Organization Convention

## Key Principles

- **Domain-driven structure**: Features organized by domain (`files/`, `git/`, `agent/`) with clear boundaries
- **Two-phase initialization**: Register bindings first, boot dependencies second
- **Mixin composition**: Services compose behavior through mixins rather than deep inheritance
- **Lazy resolution**: Services instantiated only when first requested via `make()`

## Directory Structure

```
src/byte/
├── foundation/          # Core framework (Container, Application, Bootstrap)
├── support/            # Base classes & mixins (Service, ServiceProvider)
│   └── mixins/        # Reusable behavior (Bootable, Injectable, Eventable)
└── {domain}/          # Feature domains (files, git, agent, llm, etc.)
    ├── service/       # Business logic services
    ├── command/       # User-facing CLI commands
    ├── config.py      # Domain configuration schema
    └── service_provider.py  # Registration & boot logic
```

## Service Provider Pattern

```python
class FileServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [FileService, FileDiscoveryService]  # Auto-registered as singletons

    def commands(self) -> List[Type[Command]]:
        return [AddFileCommand, DropFileCommand]  # Auto-registered & booted

    async def boot(self) -> None:
        # Phase 2: Wire dependencies, register event listeners
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.FILE_ADDED, self.handle_file_added)
```

**Bootstrap order matters**: Core services first, domain services after. See `RegisterProviders.merge()`.

## Base Classes

- **Service**: `ABC + Bootable + Injectable + Eventable + Configurable` - business logic
- **Command**: `ABC + Bootable + Injectable + Configurable + UserInteractive` - CLI commands
- **Agent**: `ABC + Bootable + Injectable + Eventable + Configurable` - AI workflows
- **Node**: `ABC + Bootable + Configurable + Eventable` - LangGraph nodes

All implement `async def boot()` for initialization requiring container access.

## Dependency Resolution

```python
# ✅ Always use self.make()
service = self.app.make(FileService)  # From Injectable mixin

# Registration patterns
app.singleton(FileService)  # Single instance, cached
app.bind(FileService)       # New instance per make()
```

**Auto-boot**: Services implementing `Bootable` are booted on first `make()` via `ensure_booted()`.

## Event-Driven Communication

```python
# Register in ServiceProvider.boot()
event_bus.on(EventType.FILE_ADDED.value, self.handle_file_added)

# Emit from Eventable services
await self.emit(Payload(event_type=EventType.FILE_ADDED, data={"path": path}))
```

## Things to Avoid

- ❌ Direct instantiation → use `self.make(ServiceClass)`
- ❌ Global state outside Container → register as singleton
- ❌ Cross-domain concrete imports → depend on abstractions or use events
