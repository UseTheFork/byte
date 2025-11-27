# Python Language Style Guide

## Key Principles

- **Type hints mandatory**: All function signatures require `Optional[T]`, `Union[A, B]`, `List[T]`, `Dict[K, V]` from `typing` (not modern `|` syntax)
- **Async by default**: Services use `async def` for I/O; sync properties for simple getters
- **Absolute imports**: Always `from byte.domain.X import Y`; never relative imports
- **Dependency injection**: Use `await self.make(ServiceClass)` in boot/methods; never direct instantiation

## Naming Conventions

```python
# Classes: PascalCase
class FileService(Service): pass
class CommandRegistry(Service): pass

# Functions/methods/variables: snake_case
async def add_file(self, path: str) -> bool: pass
_context_files: Dict[str, FileContext] = {}

# Private: _leading_underscore
async def _notify_file_added(self, file_path: str): pass

# Constants: UPPER_SNAKE_CASE (rare)
MAX_DEPTH: int = 8
```

## Type Hints

```python
from typing import Optional, Union, List, Dict, Type, TypeVar, TYPE_CHECKING

# Standard typing - no modern union syntax
def process(data: List[str]) -> Optional[Dict[str, int]]: pass
async def add_file(self, path: Union[str, PathLike]) -> bool: pass

# TYPE_CHECKING for circular dependencies
if TYPE_CHECKING:
    from byte.container import Container

# TypeVar for generics
T = TypeVar("T")
```

## Class Structure

```python
# Pydantic models for data
class FileContext(BaseModel):
    path: Path
    mode: FileMode
    
    @property
    def language(self) -> str:
        return get_language_from_filename(str(self.path)) or "text"

# Services: ABC + mixins
class FileService(Service):  # Inherits Bootable, Injectable, Eventable, Configurable
    async def boot(self) -> None:
        self._context_files: Dict[str, FileContext] = {}
    
    async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Add a file to the active context for AI awareness.
        
        Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
        """
        pass

# Abstract base classes
class Command(ABC, Bootable, Injectable, Configurable, UserInteractive):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

## Docstrings

Brief summary, blank line, concrete usage examples. Types in signature only.

```python
async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
    """Add a file to the active context for AI awareness.
    
    Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
    Usage: `await service.add_file("src/*.py", FileMode.EDITABLE)` -> adds all Python files
    """
```

## Things to Avoid

- ❌ `T | None` → use `Optional[T]`
- ❌ Relative imports → `from byte.domain.files.service import FileService`
- ❌ Direct instantiation → use `await self.make(ServiceClass)`
- ❌ Sync methods for I/O → `async def` required
- ❌ Mutable defaults → initialize in `boot()` or use `Field(default_factory=...)`