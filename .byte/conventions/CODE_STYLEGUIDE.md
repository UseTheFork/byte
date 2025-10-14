# Code Style Guide

## Python Conventions

### General

- Python 3.12+
- Tabs for indentation
- Type hints mandatory for all function signatures
- Absolute imports from `byte.` package root

### Type Hints

```python
from typing import Optional, Union, List, Dict, Type

# Use standard typing imports
def process(data: List[str]) -> Optional[Dict[str, int]]:
    pass

# TYPE_CHECKING for circular dependencies
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from byte.container import Container
```

### Naming

- Classes: `PascalCase` (`FileService`)
- Functions/methods/variables: `snake_case` (`add_file`)
- Private members: `_leading_underscore`
- Constants: `UPPER_SNAKE_CASE` (rare, avoid globals)

### Classes

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Immutable data classes
@dataclass(frozen=True)
class Config:
    name: str
    value: int

# Abstract base classes
class Service(ABC):
    @abstractmethod
    async def boot(self) -> None:
        pass
```

### Dependency Injection

```python
class MyService(Service):
    def __init__(self, container: Container) -> None:
        self.container = container

    async def boot(self) -> None:
        self.file_service = await self.make(FileService)
```

### Async/Await

- Prefer async for I/O operations
- All service methods should be async
- Override `async def boot()` for initialization

```python
async def process_file(self, path: str) -> bool:
    """Process a file asynchronously.

    Usage: `await service.process_file("config.py")`
    """
    content = await self.read_file(path)
    return await self.write_result(content)
```

### Error Handling

```python
# Specific exceptions
try:
    result = await self.process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return None

# Graceful degradation
async def try_operation(self) -> bool:
    try:
        await self.risky_operation()
        return True
    except OperationError:
        return False

# Handle cancellation
try:
    await long_running_task()
except (KeyboardInterrupt, asyncio.CancelledError):
    logger.info("Operation cancelled")
    raise
```

## Project Structure

```
src/byte/
├── core/              # Framework code
├── domain/            # Feature domains
│   └── {domain}/
│       ├── config.py
│       ├── service_provider.py
│       ├── service/
│       ├── command/
│       └── agent/
└── tests/             # Mirror source structure
```

## Comments

Follow `COMMENT_STYLEGUIDE.md`:

- Capital letter, end with period for sentences
- Separate line above code
- Space after comment character: `# `
- Docstrings required for public functions
- Explain "why" not "what"

## Build System

- Use `uv` for all package management
- Configuration in `pyproject.toml`
- Entry point: `byte.core.cli:cli`
- Run with: `uv run byte`

## Linting

Pre-commit handles formatting automatically:

- Ruff for Python formatting and linting
- Prettier for Markdown
- Keep-sorted for maintaining sorted lists

Don't suggest running these manually.
