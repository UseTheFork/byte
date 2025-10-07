# Python Style Guide

This guide outlines Python coding standards for this project, based on established patterns in the codebase.

## Type Annotations

- **Always use type hints** for all public methods, parameters, and return values
- Use `Union[str, PathLike]` for flexible path handling
- Use `Optional[T]` for nullable values
- Import types under `TYPE_CHECKING` when needed to avoid circular imports

```python
from typing import TYPE_CHECKING, Optional, Union
from os import PathLike

if TYPE_CHECKING:
    from byte.container import Container

def process_file(path: Union[str, PathLike]) -> Optional[str]:
    pass
```

## Class Design

- **Dataclasses**: Use `@dataclass(frozen=True)` for immutable data containers
- **Abstract classes**: Use `ABC` and `@abstractmethod` for interfaces
- **Dependency injection**: Accept container in `__init__` with proper typing

```python
@dataclass(frozen=True)
class FileContext:
    path: Path
    mode: FileMode

class Command(ABC):
    def __init__(self, container: Optional["Container"] = None):
        self.container = container
```

## Documentation

- **Class docstrings**: Brief purpose + usage example
- **Method docstrings**: Purpose + usage example for public methods
- **Inline comments**: Explain complex logic, not obvious code
- **Comment style**: Follow the [Comment Style Guide](COMMENT_STYLEGUIDE.md) for formatting and placement

```python
class FileService:
    """Domain service orchestrating file operations and context management.

    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """

    def add_file(self, path: Union[str, PathLike]) -> bool:
        """Add a file to the active context with validation.

        Usage: `success = manager.add_file("config.py", FileMode.READ_ONLY)`
        """
```

## Error Handling

- **Specific exceptions**: Catch specific exceptions, not broad `Exception`
- **Graceful degradation**: Return `False`/`None` rather than raising for expected failures
- **Resource cleanup**: Use context managers when appropriate

```python
try:
    return self.path.read_text(encoding="utf-8")
except (FileNotFoundError, PermissionError, UnicodeDecodeError):
    return None
```

## Code Organization

- **Single responsibility**: Each class/method has one clear purpose
- **Dependency injection**: Use container pattern for loose coupling
- **Event-driven**: Emit events for cross-domain communication
- **Immutable data**: Prefer immutable objects where possible

## Naming Conventions

- **Classes**: PascalCase (`FileService`)
- **Methods/variables**: snake_case (`add_file`)
- **Constants**: UPPER_SNAKE_CASE (`FILE_MODE`)
- **Private members**: Leading underscore (`_files`)
# Python Style Guide

## General
- Python 3.12+ required
- Use tabs for indentation (see .editorconfig)
- Ruff for linting and formatting (see pyproject.toml)
- Type hints mandatory for function signatures

## Imports
- Organize: stdlib, third-party, local (Ruff isort with combine-as-imports)
- Use absolute imports from `byte.` package root
- TYPE_CHECKING imports for circular dependencies
- Example: `from byte.core.service.base_service import Service`

## Naming Conventions
- Classes: PascalCase (e.g., `FileService`, `CommandRegistry`)
- Functions/methods: snake_case (e.g., `async def boot()`, `get_graph()`)
- Private methods: leading underscore (e.g., `_handle_stream_event()`)
- Constants: UPPER_SNAKE_CASE (rare, prefer config classes)
- Service/Provider suffix for framework classes

## Async/Await
- Prefer async/await for I/O operations
- All service methods should be async
- Use `await self.make(ServiceClass)` for dependency injection
- Example: `file_service = await self.make(FileService)`

## Type Hints
- Required for all function signatures
- Use `Optional[T]` for nullable, `Union[A, B]` for alternatives
- Use `List`, `Dict`, `Type` from typing module
- Example: `async def execute(self, request: Any, thread_id: Optional[str] = None) -> None:`

## Class Design
- Inherit from base classes: `Service`, `Command`, `Agent`, `Node`
- Use mixins for cross-cutting concerns: `Bootable`, `Injectable`, `Eventable`, `Configurable`
- Implement required abstract methods from base classes
- Override `async def boot()` for initialization logic

## Error Handling
- Create custom exceptions inheriting from domain-specific base (e.g., `EditFormatError`)
- Use descriptive exception names (e.g., `ReadOnlyFileError`, `SearchContentNotFoundError`)
- Handle `KeyboardInterrupt` and `asyncio.CancelledError` gracefully in long-running operations

## Project Structure
- Domain-driven design: `src/byte/domain/{domain}/`
- Each domain has: `config.py`, `service_provider.py`, `service/`, `command/`
- Core framework in `src/byte/core/`
- Tests mirror source structure in `src/tests/`
