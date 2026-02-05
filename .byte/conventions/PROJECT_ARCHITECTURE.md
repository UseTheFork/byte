---
name: project-architecture
description: Directory structure, module organization, dependency patterns, separation of concerns, and architectural principles for the Byte codebase. Use when creating new domains, organizing code, or understanding the application structure.
---

# Project Architecture

## Core Principles

**Domain-driven organization** - Each feature is a self-contained package under `src/byte/{domain}/`:

- `service/` - Business logic (FileService, GitService, AgentService)
- `command/` - CLI commands (AddFileCommand, CommitCommand)
- `tools/` - LangChain tool wrappers for agent integration
- `service_provider.py` - Domain registration and wiring
- `config.py` - Domain-specific Pydantic configuration models
- `schemas.py` - Data transfer objects and validation models

**Container-based dependency injection** - All services resolve via `self.app.make(ServiceClass)`:

```python
# ✓ Correct - lazy resolution
async def handle(self):
    git_service = self.app.make(GitService)
    return await git_service.get_status()

# ✗ Wrong - direct instantiation
git_service = GitService()  # Missing container context
```

**Two-phase lifecycle** - Separate registration from initialization:

```python
class MyServiceProvider(ServiceProvider):
    def register(self) -> None:
        # Phase 1: Bind to container, no cross-service dependencies
        self.app.singleton(MyService)

    async def boot(self) -> None:
        # Phase 2: Wire dependencies and event listeners
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.MY_EVENT.value, self.handle_event)
```

**Event-driven communication** - Cross-domain coordination via EventBus:

```python
# Emit from service
payload = Payload(EventType.FILE_ADDED, {"path": file_path})
await self.emit(payload)

# Listen in provider boot
event_bus.on(EventType.FILE_ADDED.value, file_service.handle_file_added)
```

## Directory Structure

```
src/byte/
├── {domain}/                    # Self-contained feature domain
│   ├── service/                 # Business logic services
│   │   └── {domain}_service.py
│   ├── command/                 # CLI command implementations
│   │   └── {action}_command.py
│   ├── tools/                   # LangChain tool wrappers (optional)
│   │   └── {tool_name}.py
│   ├── __init__.py              # Public API exports
│   ├── config.py                # Pydantic configuration models
│   ├── schemas.py               # Data transfer objects
│   └── service_provider.py      # Registration and wiring
├── foundation/                  # Core framework
│   ├── application.py           # Main container + lifecycle
│   ├── container.py             # DI container implementation
│   ├── event_bus.py             # Event system
│   └── bootstrap/               # Application bootstrapping
├── support/                     # Shared utilities
│   ├── service.py               # Base Service class
│   ├── service_provider.py      # Base ServiceProvider class
│   ├── mixins/                  # Bootable, Eventable, UserInteractive
│   └── utils/                   # Helper functions
└── main.py                      # Entry point + provider list
```

## Module Organization Patterns

**ServiceProvider structure** - Auto-register services and commands:

```python
class FileServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [FileService, FileDiscoveryService]  # Auto-singleton

    def commands(self) -> List[Type[Command]]:
        return [AddFileCommand, DropFileCommand]  # Auto-register

    def register(self) -> None:
        # Manual bindings if needed
        pass

    async def boot(self) -> None:
        # Wire event listeners after all providers registered
        event_bus = self.app.make(EventBus)
        file_service = self.app.make(FileService)
        event_bus.on(EventType.PRE_PROMPT_TOOLKIT.value,
                     file_service.list_in_context_files_hook)
```

**Service structure** - Inherit from Service base class:

```python
class FileService(Service):  # Inherits Bootable, Eventable
    def boot(self, **kwargs) -> None:
        # Initialize state after container ready
        self._context_files: Dict[str, FileContext] = {}

    async def handle(self, **kwargs) -> Any:
        # Core business logic with lazy dependency resolution
        discovery = self.app.make(FileDiscoveryService)
        return await discovery.get_files()
```

**Command structure** - Implement Command interface:

```python
class AddFileCommand(Command):
    @property
    def name(self) -> str:
        return "add"

    @property
    def category(self) -> str:
        return "Files"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(prog=self.name, description="Add file")
        parser.add_argument("file_path", help="Path to file")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        file_service = self.app.make(FileService)
        await file_service.add_file(args.file_path, FileMode.EDITABLE)

    async def get_completions(self, text: str) -> List[str]:
        # Tab completion from discovery service
        file_service = self.app.make(FileService)
        return await file_service.find_project_files(text)
```

**Tool structure** - LangChain tools for agent integration:

```python
@tool(parse_docstring=True)
async def read_files(file_paths: list[str]) -> str:
    """Read file contents from project.

    Args:
        file_paths: MUST BE A LIST, of file paths to read

    Returns:
        File contents or error message
    """
    app = get_application()
    file_service = app.make(FileService)
    return await file_service.read_files(file_paths)
```

## Dependency Flow

**Bootstrap sequence**:

1. `Application.configure()` → creates app with base bindings
2. `ApplicationBuilder.with_providers(PROVIDERS)` → merges provider list
3. `Kernel.bootstrap()` → runs bootstrappers (env, config, register providers)
4. `RegisterProviders.bootstrap()` → calls `app.register(provider)` for each
5. `app.register()` → instantiates provider, calls `register()`, `register_services()`, `register_commands()`
6. `app.boot()` → calls `provider.boot()` for all providers
7. `app.run()` → starts interactive prompt loop

**Service resolution**:

```python
# First make() triggers boot
service = self.app.make(FileService)  # Calls ensure_booted()
# Subsequent calls return cached singleton
service2 = self.app.make(FileService)  # Same instance
```

**Event flow**:

```python
# 1. Service emits event
payload = Payload(EventType.FILE_ADDED, {"path": "main.py"})
result = await self.emit(payload)

# 2. EventBus chains listeners
for listener in listeners:
    result = await listener(current_payload)
    current_payload = result  # Chain transformations

# 3. Returns final transformed payload
```

## Separation of Concerns

**Domain boundaries**:

- `/files/` - File context management, discovery, watching
- `/git/` - Git operations, commit generation
- `/agent/` - AI agent implementations and graph execution
- `/llm/` - Model configuration and LangChain integration
- `/cli/` - Command registry, prompt toolkit, rendering
- `/knowledge/` - Convention and session context management
- `/lint/` - Code linting and validation

**Layer responsibilities**:

- **Service layer** - Business logic, no CLI/UI concerns
- **Command layer** - CLI interface, delegates to services
- **Tool layer** - LangChain wrappers, minimal logic
- **Provider layer** - Wiring only, no business logic

**Cross-domain communication**:

```python
# ✓ Event-driven - loose coupling
event_bus.on(EventType.FILE_ADDED.value, git_service.stage_file)

# ✗ Direct service calls - tight coupling
file_service.git_service.stage_file()  # Avoid
```

## Application Entry Point

**main.py** - Central provider registration:

```python
PROVIDERS = [
    CLIServiceProvider,
    FileServiceProvider,
    GitServiceProvider,
    AgentServiceProvider,
    # ... all domain providers
]

def cli():
    application = Application.configure(Path.cwd(), PROVIDERS).create()
    asyncio.run(application.handle_command(sys.argv))
```

## Path Resolution

**Standardized path helpers**:

```python
app.root_path()              # Git repository root
app.base_path()              # Current working directory
app.app_path()               # Byte installation directory
app.config_path()            # .byte/ directory
app.cache_path()             # .byte/cache/
app.conventions_path()       # .byte/conventions/
app.session_context_path()   # .byte/session_context/
```

## Things to Avoid

- ❌ Business logic in ServiceProvider → delegate to services
- ❌ Cross-domain imports in services → use `self.app.make()` or events
- ❌ Resolving dependencies in `register()` → use lazy resolution in methods
- ❌ Circular dependencies → use event-driven communication
- ❌ Direct instantiation → always use container resolution
- ❌ Mixing CLI concerns in services → keep services UI-agnostic
