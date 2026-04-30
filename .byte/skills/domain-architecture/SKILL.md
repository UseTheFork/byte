---
name: domain-architecture
description: General domain architecture guide for the Byte project. Use when working within any domain under src/byte/, creating a new domain, or when you need to understand how domains are structured, how they interact, and what conventions they follow.
---

# Domain Architecture Guide

This skill documents the standard domain architecture patterns, conventions, and structure used across the Byte project. All domains live under `src/byte/<domain>/`.

## Domain Categories

There are two categories of top-level packages in `src/byte/`:

### Standard Domains
Standard domains follow the full service provider pattern. They have a `service_provider.py` and register services, commands, tools, and event listeners through the two-phase lifecycle. Examples: `git`, `files`, `llm`, `knowledge`, `tools`, `workflow`, `command`, `event`, `node`.

### Infrastructure / Support Layers
Infrastructure layers provide shared utilities, base classes, or cross-cutting concerns. They do **not** have a service provider and are consumed by standard domains as dependencies. Examples: `orchestration`, `support`, `logging`, `parsing`, `config`.

When working in the codebase, identify which category a package falls into before making changes. Standard domains follow the patterns below; infrastructure layers have their own conventions.

---

## Standard Domain Directory Layout

A standard domain follows this structure. All building blocks are **optional** — a domain only includes what it needs:

```
src/byte/<domain>/
├── __init__.py              # Public API exports (lazy imports)
├── service_provider.py      # Domain entry point — wires everything together
├── config.py                # Pydantic BaseModel for domain configuration
├── schemas.py               # Pydantic models for structured data (e.g., LLM output)
├── models.py                # Domain-specific data models (Pydantic, enums, dataclasses)
├── events.py                # Event definitions (dataclass-based, grouped under namespace)
├── service/                 # Business logic services
│   ├── primary_service.py
│   └── secondary_service.py
├── command/                 # CLI slash commands
│   └── some_command.py
├── tools/                   # Agent tools (LLM-invokable)
│   └── some_tool.py
└── validators/              # Optional validation logic
    └── some_validator.py
```

---

## Building Blocks

### ServiceProvider (`service_provider.py`)

The **entry point** for every standard domain. Extends `ServiceProvider` (from `byte.support.service_provider`). Responsible for declaring and wiring all domain components through a two-phase lifecycle:

**Phase 1 — Registration** (called during `app.register()`):
- `services()` → Return list of `Service` classes (auto-registered as singletons)
- `commands()` → Return list of `Command` classes (auto-registered as transient/bind)
- `tools()` → Return list of `BaseTool` classes (auto-registered with `ToolRegistryService`)
- `register()` → Optional override for custom bindings (e.g., `self.app.bind(...)`, `self.app.singleton(...)`)

**Phase 2 — Boot** (called after ALL providers are registered):
- `boot()` → Wire cross-service dependencies, register event listeners, start background tasks

```python
from typing import List, Type
from byte import Command, Service, ServiceProvider
from byte.my_domain import MyService, MyCommand, MyTool

class MyDomainServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [MyService]

    def commands(self) -> List[Type[Command]]:
        return [MyCommand]

    def tools(self) -> List[Type[BaseTool]]:
        return [MyTool]

    async def boot(self):
        event_bus = self.app.make(EventBus)
        event_bus.on(SomeEvents.SomeEvent, self.some_handler)
```

**Key rules:**
- Never instantiate services in `register()` or `services()`/`commands()`/`tools()` — only declare types
- In `boot()`, you can safely resolve other domains' services via `self.app.make()`
- Services returned by `services()` are automatically registered as **singletons**
- Commands returned by `commands()` are automatically registered as **transient** (bind) and wired into `CommandRegistryService`
- Tools returned by `tools()` are automatically registered with `ToolRegistryService`

### Service (`service/*.py`)

Core business logic lives in services. Each service extends `Service` (ABC + Bootable + Eventable).

```python
from byte import Service

class MyService(Service):
    def boot(self):
        # Initialize resources, resolve dependencies
        self.some_dep = self.app.make(SomeDependency)

    async def handle(self, *args, **kwargs):
        # Optional: core service operation
        pass
```

**Key rules:**
- Services are **singletons** — one shared instance per container
- Use `boot()` for initialization that requires the container (resolving dependencies, reading config)
- Access the container via `self.app`
- Services can mix in `Notifiable` and `UserInteractive` for TUI interaction
- Services can also define custom async methods beyond `handle()` for domain-specific operations

### Command (`command/*.py`)

Slash commands exposed to the user in the TUI. Each command extends `Command` (ABC + Bootable + UserInteractive + Notifiable + Eventable).

```python
from argparse import Namespace
from byte import ByteArgumentParser, Command

class MyCommand(Command):
    @property
    def name(self) -> str:
        return "mycommand"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Description of what the command does",
        )
        # Add arguments here
        return parser

    def boot(self, *args, **kwargs) -> None:
        self.my_service = self.app.make(MyService)

    async def execute(self, args: Namespace, raw_args: str) -> None:
        # Command logic here
        pass
```

**Key rules:**
- Commands are **transient** — new instance per invocation
- The `name` property defines the slash command name (e.g., `"commit"` → `/commit`)
- Use `boot()` to resolve service dependencies from the container
- Implement `execute()` for the command logic
- Use `self.emit_tui(...)` and `self.notify_*()` for user interaction

### Tool (`tools/*.py`)

Agent-invokable tools for the LLM. Each tool extends `BaseTool` (ABC + Bootable).

```python
from byte.tools import BaseTool, ToolResult

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "Description of what the tool does"
    input_schema = {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Description of the parameter",
            },
        },
        "required": ["param"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    async def run(self, param: str = "", **kwargs) -> ToolResult:
        my_service = self.app.make(MyService)
        # Tool logic here
        return ToolResult(result={"content": "result"})
```

**Key rules:**
- Tools define `name`, `description`, and `input_schema` as class attributes
- `input_schema` follows JSON Schema format
- Implement `run()` for the tool logic — receives kwargs matching the input schema
- Implement `format_tool_message()` to format the result for the LLM
- Access the container via `self.app`

### Config (`config.py`)

Domain configuration as Pydantic `BaseModel` subclasses. Registered on the top-level `ByteConfig` and accessible via `self.app["config"]`.

```python
from pydantic import BaseModel, Field

class MyDomainConfig(BaseModel):
    some_setting: bool = Field(default=True, description="What this setting controls")
    items: list[str] = Field(default_factory=list, description="List of items")
```

**Key rules:**
- Always use `Field(...)` with `default` and `description`
- Keep config flat or use nested `BaseModel` subclasses for grouping
- Access in services/commands via `self.app["config"].my_domain`

### Schemas (`schemas.py`)

Pydantic models for structured data — typically used as LLM output schemas or data transfer objects.

```python
from pydantic import BaseModel, Field

class MySchema(BaseModel):
    field: str = Field(..., description="Description for the LLM")
```

### Models (`models.py`)

Domain-specific data models — enums, Pydantic models, or dataclasses for internal domain state.

```python
from enum import Enum
from pydantic import BaseModel

class MyMode(Enum):
    OPTION_A = "option_a"
    OPTION_B = "option_b"

class MyModel(BaseModel):
    name: str
    mode: MyMode
```

### Events (`events.py`)

Events are dataclass-based, extend `Event`, and are grouped under a **namespace class** for organization.

```python
from dataclasses import dataclass
from byte.event import Event

class MyDomainEvents:
    """Namespace for all my-domain event types."""

    @dataclass
    class SomethingHappened(Event):
        """Event emitted when something happens."""
        some_field: str
        another_field: str

    @dataclass
    class SomethingElse(Event):
        """Event emitted when something else happens."""
        data: str
```

**Key rules:**
- Always use a namespace class (e.g., `FileEvents`, `SystemEvents`, `OrchestrationEvents`)
- Events are `@dataclass` classes extending `Event`
- Event listeners are registered in the service provider's `boot()` method via `EventBus.on()`
- Reference events as `MyDomainEvents.SomethingHappened`

---

## Public API & `__init__.py`

Each domain's `__init__.py` defines the public API — the classes other domains are allowed to import. Use lazy dynamic imports via `_dynamic_imports` and `import_attr` for performance.

**Key rules:**
- Export all public classes (services, commands, tools, events, models, config) from the domain root
- Other domains import from the domain root: `from byte.git import GitService, CommitCommand`
- Add entries to `__all__`, `_dynamic_imports`, and the `TYPE_CHECKING` block when adding new exports

---

## Cross-Domain Communication

**Rules:**
- **Always resolve via the container** — use `self.app.make(ServiceClass)` to get services from other domains
- **Use the EventBus** for decoupled communication — emit events and register listeners
- **Never import implementation details across domains** — only import from a domain's public `__init__.py`
- **Never directly instantiate** another domain's classes — always go through the container

---

## Creating a New Domain — Checklist

1. Create the domain directory: `src/byte/<domain>/`
2. Create `__init__.py` with public exports (lazy imports)
3. Create `service_provider.py` extending `ServiceProvider`
4. Add building blocks as needed:
   - `service/` — for business logic
   - `command/` — for slash commands
   - `tools/` — for agent tools
   - `config.py` — for configuration
   - `schemas.py` — for structured data models
   - `models.py` — for domain data models
   - `events.py` — for domain events
5. Register the service provider with the application (in `Application.configure()` providers list)
6. Declare services/commands/tools in the service provider's `services()`, `commands()`, `tools()` methods
7. Wire cross-domain dependencies and event listeners in `boot()`

