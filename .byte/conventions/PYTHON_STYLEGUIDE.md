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
