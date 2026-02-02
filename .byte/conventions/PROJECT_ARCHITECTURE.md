# Project Architecture Convention

## Key Principles

- **Domain-driven module organization**: Each feature domain (files, git, agent, llm) is a self-contained package under `src/byte/`
- **Service Provider pattern**: Every domain has a `ServiceProvider` that registers services, commands, and event listeners
- **Dependency injection via Container**: All services receive `app: Application` parameter and resolve dependencies via `self.app.make(ServiceClass)`
- **Two-phase lifecycle**: `register()` binds services to container, `boot()` wires up cross-domain dependencies and event listeners

## Directory Structure

```
src/byte/
├── {domain}/              # Self-contained feature domain
│   ├── service/           # Business logic services
│   ├── command/           # CLI command implementations
│   ├── tools/             # LangChain tool wrappers (if applicable)
│   ├── __init__.py        # Public API exports
│   ├── config.py          # Domain-specific configuration models
│   ├── service_provider.py  # Domain registration and wiring
│   └── schemas.py         # Pydantic models for domain data
├── foundation/            # Core framework (Application, Container, EventBus)
├── support/               # Shared utilities and base classes
└── main.py                # Application entry point
```

## Module Organization Patterns

**Service Provider structure:**

```python
class MyDomainServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [MyService, OtherService]  # Auto-registered as singletons

    def commands(self) -> List[Type[Command]]:
        return [MyCommand]  # Registered with CommandRegistry

    def register(self) -> None:
        # Bind services to container (called during bootstrap)
        pass

    async def boot(self) -> None:
        # Wire up event listeners and cross-domain dependencies
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.MY_EVENT.value, self.handle_event)
```

**Service structure:**

```python
class MyService(Service):  # Inherits Bootable, Eventable
    def boot(self, **kwargs) -> None:
        # Initialize after container is ready
        self._cache = {}

    async def handle(self, **kwargs) -> Any:
        # Core business logic
        other = self.app.make(OtherService)
        return await other.process()
```

## Dependency Flow

1. **Bootstrap phase**: `Application.configure()` → registers providers → calls `provider.register()`
2. **Boot phase**: `app.boot()` → calls `provider.boot()` → wires event listeners
3. **Runtime**: Services resolved lazily via `app.make(Service)` → auto-booted via `ensure_booted()`
4. **Cross-domain communication**: Via `EventBus` with typed `Payload` objects

## Separation of Concerns

- **`/service/`**: Business logic, no CLI or presentation concerns
- **`/command/`**: CLI interface, delegates to services
- **`/tools/`**: LangChain tool wrappers for agent integration
- **`config.py`**: Pydantic models for domain configuration
- **`schemas.py`**: Data transfer objects and validation models
- **`service_provider.py`**: Wiring and registration only, no business logic

## Import Conventions

```python
# Public API via __init__.py
from byte import Application, Service, EventBus  # Lazy-loaded via __getattr__

# Internal imports use full paths
from byte.files.service.file_service import FileService
from byte.agent import AgentService
```

## Things to Avoid

- ❌ Cross-domain imports in service logic → use `self.app.make()` for loose coupling
- ❌ Business logic in ServiceProvider → delegate to services
- ❌ Direct instantiation → always use container resolution
- ❌ Circular dependencies → use event-driven communication instead
