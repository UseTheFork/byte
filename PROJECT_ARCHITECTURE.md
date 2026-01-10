Now I have enough information to create a comprehensive architecture convention document. Let me create a focused, scannable document that captures the key architectural patterns.

---

# Directory Structure & Module Organization Convention

## Key Principles

- **Domain-driven structure**: Features organized by domain (`files/`, `git/`, `agent/`) with clear boundaries
- **Two-phase initialization**: Register bindings first, boot dependencies second (prevents circular dependency issues)
- **Mixin composition over inheritance**: Services compose behavior via `Bootable`, `Injectable`, `Eventable`, `Configurable`
- **Container-based DI**: All dependencies resolved through container, never direct instantiation

## Directory Structure Pattern

```
src/byte/
├── foundation/           # Core framework (Container, Application, EventBus)
│   ├── bootstrap/       # Bootstrappers for app initialization phases
│   └── console/         # Console kernel and CLI application
├── support/             # Base classes and mixins
│   ├── mixins/         # Reusable behavior (Bootable, Injectable, etc.)
│   └── service.py      # Base Service class
└── {domain}/            # Feature domains (files, git, agent, llm, etc.)
    ├── service/        # Business logic services
    ├── command/        # User-facing slash commands
    ├── config.py       # Domain configuration schema
    └── service_provider.py  # Registration & boot orchestration
```

## Service Provider Pattern

Each domain has a `ServiceProvider` that encapsulates registration:

```python
class FileServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        # Auto-registered as singletons
        return [FileIgnoreService, FileDiscoveryService, FileService]

    def commands(self) -> List[Type[Command]]:
        # Auto-registered as transient + added to CommandRegistry
        return [AddFileCommand, DropFileCommand, ListFilesCommand]

    def register(self) -> None:
        # Phase 1: Register bindings only (optional override)
        pass

    async def boot(self) -> None:
        # Phase 2: Wire dependencies, register event listeners
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.PRE_PROMPT, self.hook_method)
```

**Bootstrap order matters**: Core services first (`foundation`, `support`), domain services after.

## Base Class Hierarchy

- **Service**: `ABC + Bootable + Injectable + Eventable + Configurable` - business logic
- **Command**: `ABC + Bootable + Injectable + Configurable + UserInteractive` - user commands
- **Agent**: `ABC + Bootable + Injectable + Eventable + Configurable` - AI workflows
- **Node**: `ABC + Bootable + Configurable + Eventable` - LangGraph nodes

All implement `boot()` for initialization requiring container access.

## Dependency Resolution

```python
# ❌ NEVER: Direct instantiation
service = FileService(container)

# ✅ ALWAYS: Resolve via container
service = self.app.make(FileService)  # From Injectable mixin

# Registration patterns
self.app.singleton(FileService)  # Single instance
self.app.bind(Command)           # New instance per resolution
```

## Event-Driven Communication

Decouples domains without tight coupling:

```python
# In ServiceProvider.boot()
event_bus = self.app.make(EventBus)
event_bus.on(EventType.FILE_ADDED, self.handle_file_added)

# From Eventable services
await self.emit(Payload(event_type=EventType.FILE_ADDED, data={...}))
```

## Things to Avoid

- ❌ Direct instantiation (`FileService()`) → use `self.app.make(ServiceClass)`
- ❌ Synchronous I/O in `__init__` → use `async def boot()`
- ❌ Accessing services in `register()` → wait for `boot()` phase
- ❌ Cross-domain concrete imports → depend on abstractions or use events
