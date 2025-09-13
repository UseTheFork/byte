# Byte Architecture Guide

This guide outlines the architectural patterns and structure of the Byte CLI AI assistant.

## Core Architecture

Byte follows **Domain-Driven Design** with **Dependency Injection** and **Event-Driven Architecture** patterns.

### Key Principles

- **Single Responsibility**: Each class/service has one clear purpose
- **Dependency Injection**: Services are injected via container pattern
- **Event-Driven**: Cross-domain communication via domain events
- **Immutable Data**: Prefer frozen dataclasses for data containers
- **Automatic Mixin Initialization**: Mixins self-boot via `boot_{mixin_name}` methods

## Project Structure

```
byte/
├── core/                    # Framework-level infrastructure
│   ├── command/            # Command pattern implementation
│   ├── events/             # Event system (Observer pattern)
│   └── ui/                 # User interface components
├── domain/                 # Business logic domains
│   ├── files/              # File context management
│   ├── commit/             # Git commit functionality
│   ├── llm/                # Language model integration
│   └── system/             # Core system commands
├── cli/                    # CLI entry point
└── container.py            # Dependency injection container
```

## Architectural Patterns

### 1. Service Provider Pattern

Each domain registers its services via a `ServiceProvider`:

```python
class FileServiceProvider(ServiceProvider):
    def register(self, container: Container) -> None:
        # Phase 1: Register service bindings
        container.bind("file_service", lambda: FileService(...))

    def boot(self, container: Container) -> None:
        # Phase 2: Configure relationships after all services registered
        command_registry.register_slash_command(...)
```

### 2. Command Pattern

User interactions are handled via commands:

```python
class AddFileCommand(Command, Eventable):
    @property
    def name(self) -> str:
        return "add"

    async def execute(self, args: str) -> None:
        # Mixins boot automatically
        await self.event(FileAdded(file_path=args))
```

### 3. Repository Pattern

Data persistence abstracted via interfaces:

```python
class FileRepositoryInterface(ABC):
    @abstractmethod
    def save(self, file_context: FileContext) -> bool:
        pass
```

### 4. Event-Driven Communication

Domains communicate via events to maintain loose coupling:

```python
@dataclass
class FileAdded(Event):
    file_path: str = ""
    mode: FileMode = FileMode.READ_ONLY

# Usage
await self.event(FileAdded(file_path="main.py"))
```

### 5. Mixin Boot Pattern

Mixins automatically initialize via boot methods called by base classes:

```python
class Eventable:
    def boot_eventable(self) -> None:
        """Auto-called by Command.__init__."""
        event_dispatcher = self.container.make("event_dispatcher")
        self._event_dispatcher = event_dispatcher

class ExitCommand(Command, Eventable):
    # No manual boot() needed - boot_eventable() called automatically
```

## Dependency Flow

1. **Bootstrap** (`bootstrap.py`) - Initializes container and service providers
2. **Container** (`container.py`) - Manages service bindings and resolution
3. **Service Providers** - Register domain services in two phases
4. **Commands** - Handle user interactions via command pattern
5. **Services** - Orchestrate business logic within domains

## Key Components

### Container (`byte/container.py`)
- Simple dependency injection container
- Singleton and transient service lifetimes
- Global `app` instance for application-wide access

### Command Registry (`byte/core/command/registry.py`)
- Central command discovery and routing
- Supports slash commands (`/add`) and @ commands
- Tab completion and help system integration

### Event System (`byte/core/events/`)
- Observer pattern for domain events
- Async/sync listener support
- Isolated failure handling

### File Context (`byte/domain/files/`)
- Manages AI-aware file state
- Read-only vs editable permissions
- Context generation for AI prompts

## Initialization Flow

1. **Bootstrap** registers all service providers
2. **Register Phase** - All services bind to container
3. **Boot Phase** - Services configure relationships
4. **Main Loop** - CLI processes user input via commands

## Extension Points

- **New Commands**: Extend `Command` class with mixins - boot methods called automatically
- **New Domains**: Create domain folder with service provider
- **New Events**: Extend `Event` class and emit via `Eventable` mixin
- **New LLM Providers**: Implement `LLMService` interface

## Best Practices

- Use type hints for all public interfaces
- Document classes with purpose + usage examples
- Emit events for cross-domain communication
- Prefer immutable data structures
- Handle errors gracefully with specific exceptions
- Use `boot_{mixin_name}` pattern for automatic mixin initialization
- Follow the [Python Style Guide](PYTHON_STYLEGUIDE.md) for code formatting and structure
- Follow the [Comment Style Guide](COMMENT_STYLEGUIDE.md) for documentation and comments
