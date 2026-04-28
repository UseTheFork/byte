---
name: foundation-domain
description: Coding guidance for the foundation domain. Use when working within src/byte/foundation/ or when other domains need to interact with the foundation layer (container, application, paths, config, environment, service providers, task management).
---


# Foundation Domain Guide

The foundation domain (`src/byte/foundation/`) is the core infrastructure layer of the Byte application. It provides the DI container, application lifecycle, path management, environment detection, exception hierarchy, and task management.

## Domain Structure

```
src/byte/foundation/
├── __init__.py                  # Public API: Application, Container, Kernel, TaskManager, ByteException, FoundationServiceProvider
├── application.py               # Main app container (extends Container)
├── application_builder.py       # Fluent builder for configuring the app
├── container.py                 # DI container with singleton/transient lifetimes
├── environment_detector.py      # Resolves app environment (CLI → env var → config)
├── exceptions.py                # Base exception hierarchy
├── service_provider.py          # Registers core singletons (ByteTUI, EventBus, TaskManager)
├── task_manager.py              # Background async task management
├── bootstrap/                   # Application initialization pipeline
│   └── ...
└── console/                     # Console kernel and application
    └── ...
```

## Key Patterns & Conventions

### Container (DI)

The `Container` class is the core dependency injection mechanism. It supports three lifetime types:

- **`singleton(ServiceClass)`** — One shared instance, created lazily on first `make()` call, then cached.
- **`bind(ServiceClass)`** — Transient; a new instance is created on every `make()` call.
- **`instance("key", value)`** — Directly register a pre-built instance (always shared).

```python
# Registration
self.app.singleton(FileService)          # Singleton (lazy)
self.app.bind(ParseBlocksNode)           # Transient (new each time)
self.app.instance("config", config_obj)  # Direct instance

# Resolution
file_service = self.app.make(FileService)  # Resolves by class
config = self.app["config"]                # Resolves by string key (shorthand)
```

**Lifetime rules:**
- **Services** → always `singleton` (stateful, shared)
- **Nodes** → always `bind` / transient (stateless, per-execution)
- **Agents** → always `singleton` (contain compiled graphs)
- **Commands** → transient (per invocation)

**Auto-injection:** When no factory is provided, the container auto-creates instances by calling `ServiceClass(app=self)`. Classes resolved from the container that extend `Bootable` will have `ensure_booted()` called automatically after construction.

### Well-Known Container Bindings

These string keys are registered during bootstrap and are always available after the kernel bootstraps:

| Key | Type | Description |
|---|---|---|
| `"app"` | `Application` | The application instance itself |
| `"config"` | `ByteConfig` | Parsed application configuration (Pydantic model) |
| `"env"` | `str` | Current environment name (`"development"`, `"production"`, `"testing"`) |
| `"args"` | `Repository` | Parsed CLI arguments (raw, flags, options, positional) |
| `"version"` | `str` | Application version from package metadata |
| `"path"` | `Path` | Git repository root (alias for `"path.root"`) |
| `"path.root"` | `Path` | Git repository root |
| `"path.app"` | `Path` | Byte package installation directory |
| `"path.config"` | `Path` | `.byte/` directory |
| `"path.cache"` | `Path` | `.byte/cache/` directory |
| `"path.conventions"` | `Path` | `.byte/conventions/` directory |
| `"path.session_context"` | `Path` | `.byte/session_context/` directory |

Access via bracket syntax:
```python
config = self.app["config"]
root = self.app["path.root"]
env = self.app["env"]
```

The container also provides typed overloads for `__getitem__` so type checkers can infer return types for these well-known keys.

### Application

`Application` extends `Container` and adds:

- **Path helpers** — `root_path()`, `config_path()`, `cache_path()`, `conventions_path()`, `skills_path()`, `session_context_path()`, `app_path()`, `base_path()`. All accept an optional sub-path string to append.
- **Environment checks** — `is_development()`, `is_production()`, `running_unit_tests()`.
- **Provider registration** — `app.register(MyServiceProvider)` validates the class extends `ServiceProvider`, registers it as a singleton, instantiates it, and calls `register()`, `register_services()`, `register_commands()`, and `register_tools()` in sequence.
- **Boot lifecycle** — `app.boot()` iterates all registered providers and calls their async `boot()` method. Fires `_booting_callbacks` before and `_booted_callbacks` after.
- **Task dispatch** — `app.dispatch_task(coro)` delegates to `TaskManager` for fire-and-forget background tasks.
- **TUI access** — `app.tui()` resolves `ByteTUI`, `app.emit_tui(message)` posts messages to the TUI conversation panel.

**Creating an application:**
```python
from byte.foundation import Application

app = Application.configure(base_path=Path.cwd(), providers=[...]).create()
```
This uses the `ApplicationBuilder` fluent pattern: `with_kernels()` → `with_providers(providers)` → `create()`.

### Service Providers

The `FoundationServiceProvider` registers the core singletons:
- `ByteTUI` — Terminal UI
- `EventBus` — Event-driven communication bus
- `TaskManager` — Background async task management (eagerly instantiated via `make()`)

When writing a new service provider for another domain that interacts with foundation:

```python
class MyDomainServiceProvider(ServiceProvider):
    def register(self) -> None:
        # Register bindings — no instantiation here
        self.app.singleton(MyService)

    async def boot(self) -> None:
        # Wire up cross-service dependencies after all providers are registered
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.SOME_EVENT, self._handler)
```

### Exception Hierarchy

All custom exceptions must inherit from `ByteException`:

```python
from byte.foundation.exceptions import ByteException, ByteConfigException

class ByteException(Exception):       # Base for all Byte errors
class ByteConfigException(ByteException):  # Configuration-related errors
```

When adding domain-specific exceptions, extend `ByteException` (or `ByteConfigException` for config errors).

### TaskManager

`TaskManager` manages named background async tasks:

```python
task_manager = self.app.make(TaskManager)

# Named task (can be stopped/replaced by name)
task_manager.start_task("watcher", some_coroutine())
task_manager.stop_task("watcher")

# Fire-and-forget (auto-named)
self.app.dispatch_task(some_coroutine())

# Graceful shutdown
await task_manager.shutdown()
```

### Environment Detection

The `EnvironmentDetector` resolves the environment with this priority:
1. CLI argument `--env <value>`
2. `BYTE_ENV` environment variable
3. Config callback (from `config.app.env`)

### Interacting with Foundation from Other Domains

- **Always resolve via the container** — never import and instantiate foundation classes directly in domain code.
- **Use `self.app`** — all services, commands, and providers receive the app container.
- **Access paths via bindings** — use `self.app["path.root"]` or `self.app.root_path("subdir")`.
- **Access config via binding** — use `self.app["config"]` to get the `ByteConfig` instance.
- **Do not import across domains** — use the container for cross-domain dependencies. This is a core architectural anti-pattern to avoid.

### Imports

Always import foundation types from the domain root:
```python
from byte.foundation import Application, Container, Kernel, TaskManager, ByteException
```

The `__init__.py` uses lazy dynamic imports via `_dynamic_imports` and `import_attr`. When adding new public exports to the foundation domain, add entries to both `__all__`, `_dynamic_imports`, and the `TYPE_CHECKING` block.

