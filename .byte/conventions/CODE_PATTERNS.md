---
name: code-patterns
description: Common design patterns, error handling, async/await patterns, dependency injection, and recurring code structures in the Byte codebase. Use when implementing new services, agents, commands, or cross-domain features.
---

# Code Patterns Convention

## Dependency Injection

**Container-based resolution** - Never instantiate services directly:

```python
# ✓ Correct
other_service = self.app.make(OtherService)
result = await other_service.process()

# ✗ Wrong
other_service = OtherService()  # Missing container context
```

**Service registration** - Auto-register as singletons via `services()`:

```python
class MyServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [MyService, OtherService]  # Automatically bound as singletons
```

**Manual binding** - Use `singleton()` or `bind()` in `register()`:

```python
def register(self) -> None:
    self.app.singleton(EventBus)  # Single instance
    self.app.bind(Node)  # New instance per resolution
```

## Two-Phase Initialization

**Phase 1: Register** - Bind services to container, no dependencies:

```python
def register(self) -> None:
    self.app.singleton(MyService)
    # No cross-service dependencies here
```

**Phase 2: Boot** - Wire dependencies and event listeners:

```python
async def boot(self) -> None:
    event_bus = self.app.make(EventBus)
    event_bus.on(EventType.MY_EVENT.value, self.handle_event)
```

**Service boot** - Initialize state after container ready:

```python
class MyService(Service):
    def boot(self, **kwargs) -> None:
        self._cache = {}  # Initialize after container ready
        # Don't resolve dependencies here - use lazy resolution in methods
```

**Lazy resolution with auto-boot** - Services boot on first `make()`:

```python
async def handle(self, **kwargs) -> Any:
    # Service auto-boots via ensure_booted() on first make()
    other = self.app.make(OtherService)
    return await other.process()
```

## Async/Await Patterns

**All service methods are async** - Even if not awaiting internally:

```python
async def add_file(self, path: str, mode: FileMode) -> bool:
    # Async for consistency and future-proofing
    self._context_files[path] = FileContext(path, mode)
    return True
```

**Validate-then-handle pattern** - Service base class enforces:

```python
async def __call__(self, **kwargs) -> Any:
    await self.validate()  # Check preconditions
    return await self.handle(**kwargs)  # Execute logic
```

**Conditional async execution** - Check if callback is coroutine:

```python
for callback in self._booted_callbacks:
    if inspect.iscoroutinefunction(callback):
        await callback(self)
    else:
        callback(self)
```

**Background tasks** - Fire-and-forget with TaskManager:

```python
self.app.dispatch_task(some_async_function())  # Auto-managed lifecycle
```

## Error Handling

**Domain-specific exceptions** - Inherit from `ByteException`:

```python
class ByteAgentException(ByteException):
    pass

class DummyNodeReachedException(ByteAgentException):
    """Raised when execution reaches unimplemented node."""
    pass
```

**Return False/None for expected failures** - Not exceptions:

```python
async def add_file(self, path: str, mode: FileMode) -> bool:
    if not path_obj.is_file():
        return False  # Expected failure, not exceptional
    # ...
    return True
```

**Retry loops with user confirmation** - For recoverable errors:

```python
continue_commit = True
while continue_commit:
    try:
        commit = self._repo.index.commit(commit_message)
        continue_commit = False  # Success, exit loop
    except Exception as e:
        console.print_error_panel(f"Failed: {e}")
        retry = await self.prompt_for_confirmation("Try again?", default=True)
        if not retry:
            continue_commit = False
```

**Catch specific exceptions** - Never broad `Exception` in production:

```python
try:
    repo = Repo(self._base_path, search_parent_directories=True)
except InvalidGitRepositoryError:  # Specific exception
    raise RuntimeError(f"No Git repository found at {self._base_path}")
```

**Graceful degradation in event listeners** - Log and continue:

```python
for listener in self._listeners[event_name]:
    try:
        result = await listener(current_payload)
    except Exception as e:
        self.app["log"].exception(e)  # Log but don't break event chain
        print(f"Error in listener for '{event_name}': {e}")
```

## Event-Driven Communication

**Emit events from Eventable services** - Use typed Payload:

```python
payload = Payload(
    event_type=EventType.FILE_ADDED,
    data={"file_path": file_path, "mode": mode.value}
)
await self.emit(payload)
```

**Register listeners in ServiceProvider.boot()** - Not in service boot:

```python
async def boot(self) -> None:
    event_bus = self.app.make(EventBus)
    file_service = self.app.make(FileService)
    event_bus.on(
        EventType.PRE_PROMPT_TOOLKIT.value,
        file_service.list_in_context_files_hook
    )
```

**Transform payloads in hooks** - Return modified payload:

```python
async def list_in_context_files_hook(self, payload: Payload) -> Payload:
    info_panel = payload.get("info_panel", [])
    info_panel.append(self._create_file_panel())
    return payload.set("info_panel", info_panel)
```

**Payload chaining** - Each listener receives previous result:

```python
async def emit(self, payload: Payload) -> Payload:
    current_payload = payload
    for listener in self._listeners[event_name]:
        result = await listener(current_payload)
        if result is not None:
            current_payload = result  # Chain transformations
    return current_payload
```

## Common Patterns

**Wildcard path support** - Check for glob characters:

```python
if "*" in path_str or "?" in path_str or "[" in path_str:
    matching_paths = glob.glob(str(pattern_path), recursive=True)
    # Process multiple matches
else:
    # Handle single path
```

**Lazy initialization** - Build expensive objects on first access:

```python
async def get_checkpointer(self) -> InMemorySaver:
    if self._checkpointer is None:
        self._checkpointer = InMemorySaver()
    return self._checkpointer
```

**Property-based computed values** - Use `@property` for derived state:

```python
@property
def name(self) -> str:
    return "add"

@property
def category(self) -> str:
    return "Files"
```

**Mixin composition** - Services inherit behavior from mixins:

```python
class Service(ABC, Bootable, Eventable):
    # Composes boot lifecycle and event emission
    pass

class GitService(Service, UserInteractive):
    # Adds user interaction capabilities
    pass
```

**Path resolution** - Always resolve relative to project root:

```python
if not Path(path).is_absolute():
    path_obj = (self.app.root_path(str(path))).resolve()
else:
    path_obj = Path(path).resolve()
```

**Filtering with optional parameters** - Return all if None:

```python
def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
    files = list(self._context_files.values())
    if mode is not None:
        files = [f for f in files if f.mode == mode]
    return sorted(files, key=lambda f: f.relative_path)
```

## Things to Avoid

- ❌ Direct instantiation → use `self.app.make(ServiceClass)`
- ❌ Sync methods in services → all service methods should be async
- ❌ Booting in `__init__` → use `boot()` for container-dependent setup
- ❌ Broad exception catching → catch specific exceptions only
- ❌ Cross-domain imports in services → use `self.app.make()` for loose coupling
- ❌ Business logic in ServiceProvider → delegate to services
- ❌ Resolving dependencies in `boot()` → use lazy resolution in methods
