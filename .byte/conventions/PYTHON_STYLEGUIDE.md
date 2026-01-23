# Python Style Guide

## General

- Python 3.12+, **spaces** for indentation, Ruff for linting/formatting
- Type hints mandatory for all function signatures
- Absolute imports from `byte.` package root

## Type Hints & Imports

- Use `Optional[T]`, `Union[A, B]`, `List`, `Dict`, `Type` from typing

## Naming

- Classes: `PascalCase` (`FileService`); Methods/vars: `snake_case` (`add_file`)
- Private: `_leading_underscore`; Constants: `UPPER_SNAKE_CASE` (rare)

## Class Design

- Dataclasses: `@dataclass(frozen=True)` for immutable data
- Abstract: `ABC` + `@abstractmethod` for interfaces
- Inherit base classes: `Service`, `Command`, `Agent`, `Node`
- Use mixins: `Bootable`, `Injectable`, `Eventable`, `Configurable`
- Dependency injection: Accept container in `__init__`, use `await self.app.make(ServiceClass)`

## Async/Await

- Prefer async/await for I/O; all service methods should be async
- Override `async def boot()` for initialization

## Error Handling

- Catch specific exceptions, not broad `Exception`
- Graceful degradation: return `False`/`None` for expected failures
- Custom exceptions inherit from domain base: `EditFormatError`, `ReadOnlyFileError`
- Handle `KeyboardInterrupt` and `asyncio.CancelledError` in long-running operations

## Architecture

- Domain-driven: `src/byte/domain/{domain}/` with `config.py`, `service_provider.py`, `service/`, `command/`
- Single responsibility, dependency injection via container, event-driven communication
- Core framework in `src/byte/core/`; tests mirror source in `src/tests/`
