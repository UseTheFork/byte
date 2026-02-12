---
name: project-architecture
description: Architecture patterns for directory structure, module organization, dependency injection, separation of concerns, and service provider pattern. Use when creating new modules, services, or understanding the codebase structure.
---

# Project Architecture

## Directory Structure

### Domain-Driven Module Organization

```
src/byte/{domain}/
├── command/          # CLI commands for this domain
├── service/          # Business logic services
├── tools/            # LangChain tools (if domain provides AI tools)
├── validators/       # Domain-specific validators
├── __init__.py       # Public API exports
├── config.py         # Domain configuration schema
├── schemas.py        # Pydantic models
├── service_provider.py  # DI registration
└── exceptions.py     # Domain-specific exceptions
```

**Key principles:**

- Each domain is self-contained under `src/byte/{domain}/`
- `service_provider.py` is the entry point for DI registration
- Public API exposed via `__init__.py` (import from domain root, not submodules)
- Configuration uses Pydantic models in `config.py`

### Foundation Layer

`src/byte/foundation/` contains core infrastructure:

- `Container`: DI container with singleton/transient lifetimes
- `Application`: Main app container extending Container
- `ServiceProvider`: Base class for all providers
- `bootstrap/`: Application initialization sequence

## Dependency Injection Pattern

### Container Usage

```python
# Singleton registration (shared instance)
self.app.singleton(FileService)

# Transient registration (new instance each time)
self.app.bind(ParseBlocksNode)

# Resolution
file_service = self.app.make(FileService)

# Direct instance registration
self.app.instance("config", config_instance)
```

**Lifetime rules:**

- **Services**: Always singletons (stateful, shared across app)
- **Nodes**: Always transient (stateless, created per graph execution)
- **Agents**: Always singletons (contain compiled graphs)
- **Commands**: Transient (created per invocation)

### Service Provider Pattern

```python
class DomainServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        """Services to register as singletons"""
        return [FileService, DiscoveryService]

    def commands(self) -> List[Type[Command]]:
        """Commands to register with CommandRegistry"""
        return [AddFileCommand, DropFileCommand]

    def register(self) -> None:
        """Phase 1: Register bindings (no instantiation)"""
        self.app.singleton(CustomService)

    async def boot(self) -> None:
        """Phase 2: Configure after all providers registered"""
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.FILE_ADDED, self.handle_file_added)
```

**Registration in `main.py`:**

```python
PROVIDERS = [
    CLIServiceProvider,
    FileServiceProvider,
    AgentServiceProvider,
    # ... order matters for dependencies
]

application = Application.configure(Path.cwd(), PROVIDERS).create()
```

## Separation of Concerns

### Service Layer

Services extend `Service` base class:

```python
class FileService(Service):
    async def validate(self) -> bool:
        """Pre-execution validation"""
        return True

    async def handle(self, **kwargs) -> Any:
        """Core business logic"""
        pass
```

**Service responsibilities:**

- Business logic and domain operations
- Stateful operations (maintain internal state)
- Coordinate between multiple concerns
- Always singletons

### Agent Layer

Agents extend `Agent` base class:

```python
class CoderAgent(Agent):
    async def build(self) -> CompiledStateGraph:
        """Build LangGraph state machine"""
        builder = GraphBuilder(self.app, start_node=AssistantNode)
        builder.add_node(ParseBlocksNode, goto="subprocess_node")
        return builder.build().compile(checkpointer=await self.get_checkpointer())

    def get_prompt(self):
        """Return ChatPromptTemplate"""
        pass

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        """Return LLM configuration"""
        pass
```

**Agent responsibilities:**

- Define LangGraph state machines
- Orchestrate nodes and routing logic
- Manage conversation memory via checkpointer
- Always singletons (contain compiled graphs)

### Node Layer

Nodes extend `Node` base class:

```python
class ParseBlocksNode(Node):
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Any:
        """Execute node logic"""
        # Access LLM via runtime.context
        # Modify state and return
        pass
```

**Node responsibilities:**

- Single-purpose graph operations
- Stateless (no instance variables)
- Always transient (new instance per execution)

### Command Layer

Commands extend `Command` base class:

```python
class AddFileCommand(Command):
    @property
    def name(self) -> str:
        return "add"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(description="Add files to context")
        parser.add_argument("files", nargs="+")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute command logic"""
        pass
```

**Command responsibilities:**

- CLI interface and argument parsing
- Delegate to services for business logic
- User interaction and feedback

## Architectural Principles

### Event-Driven Communication

```python
# Register listener
event_bus = self.app.make(EventBus)
event_bus.on(EventType.FILE_ADDED, self.handle_file_added)

# Emit event
payload = Payload(EventType.FILE_ADDED, {"path": file_path})
await event_bus.emit(payload)
```

**Event types in `EventType` enum:**

- `POST_BOOT`: After application boot
- `PRE_PROMPT_TOOLKIT` / `POST_PROMPT_TOOLKIT`: Around user input
- `FILE_ADDED` / `FILE_CHANGED`: File system events
- `PRE_AGENT_EXECUTION` / `POST_AGENT_EXECUTION`: Around agent execution

### Bootable Mixin Pattern

```python
class MyService(Service):  # Service extends Bootable
    def boot(self, **kwargs) -> None:
        """Called once after instantiation"""
        self._cache = {}
        self._setup_watchers()
```

**Boot sequence:**

1. `__init__`: Store app reference
2. `boot()`: Setup that requires container access
3. Service provider's `boot()`: Cross-service wiring

### Configuration Management

```python
# Domain config schema
class FilesConfig(BaseModel):
    watch: WatchConfig = Field(default_factory=WatchConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)

# Root config aggregates all domains
class ByteConfig(BaseModel):
    files: FilesConfig = Field(default_factory=FilesConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    # ...
```

**Access pattern:**

```python
config = self.app["config"]
if config.files.watch.enable:
    # ...
```

### Graph Builder Pattern

```python
builder = GraphBuilder(self.app, start_node=AssistantNode)
builder.add_node(ParseBlocksNode, goto="subprocess_node")
builder.add_node(SubprocessNode, goto="lint_node")
graph = builder.build().compile(checkpointer=checkpointer)
```

**Automatic node discovery:**

- All `Node` subclasses auto-discovered
- Unregistered nodes become `DummyNode` (no-op)
- Enables flexible routing without breaking graphs

### Path Management

```python
self.app["path.root"]          # Git repository root
self.app["path.config"]        # .byte/ directory
self.app["path.conventions"]   # .byte/conventions/
self.app["path.cache"]         # .byte/cache/
```

## Module Dependencies

**Dependency flow (top to bottom):**

```
foundation → support → {domain modules} → agent
```

- `foundation`: Core DI, Application, Container
- `support`: Mixins, utilities, base classes
- Domain modules: Independent, import from foundation/support only
- `agent`: Depends on multiple domains for tools/services

**Anti-pattern:** Domain modules should NOT import from each other directly. Use DI container for cross-domain dependencies.
