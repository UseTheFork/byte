# Code Patterns & Design Conventions

## Key Principles

- **Mixin composition over inheritance**: Services compose behavior through mixins (`Bootable`, `Injectable`, `Eventable`, `Configurable`)
- **Two-phase initialization**: Register bindings first (`register()`), boot dependencies second (`boot()`)
- **Lazy resolution with auto-boot**: Services instantiated on first `make()` call, automatically booted via `ensure_booted()`
- **Event-driven communication**: Cross-domain communication via `EventBus` with typed `Payload` objects

## Dependency Injection

```python
# Service with container injection
class MyService(Service):
    def boot(self, **kwargs) -> None:
        self._cache = {}

    async def handle(self, **kwargs) -> Any:
        other_service = self.app.make(OtherService)
        return await other_service.process()

# ServiceProvider registration
class MyServiceProvider(ServiceProvider):
    def services(self) -> List[Type[Service]]:
        return [MyService, OtherService]  # Auto-registered as singletons

    async def boot(self) -> None:
        event_bus = self.app.make(EventBus)
        event_bus.on(EventType.MY_EVENT.value, self.handle_event)
```

## Async/Await Patterns

- All service methods are async
- Use validate-then-handle pattern: `await self.validate()` then `await self.handle()`
- Handle cancellation in long-running operations with `asyncio.CancelledError`

## Error Handling

- Domain-specific exceptions inherit from `ByteException`
- Return `False`/`None` for expected failures, not exceptions
- Retry loops with user confirmation for recoverable errors
- Catch specific exceptions, never broad `Exception`

## Event Communication

```python
# Emit events from Eventable services
await self.emit(Payload(event_type=EventType.FILE_ADDED, data={...}))

# Register listeners in ServiceProvider.boot()
event_bus.on(EventType.FILE_ADDED.value, self.handle_file_added)

# Transform payloads in hooks
async def hook(self, payload: Payload) -> Payload:
    data = payload.get("key", [])
    data.extend(["new_item"])
    return payload.set("key", data)
```

## Common Patterns

- **Lazy initialization**: Cache expensive objects, build on first access
- **Wildcard support**: Check for `*`, `?`, `[` in paths, use `glob.glob()`
- **Property-based computed values**: Use `@property` for derived attributes
- **Graceful degradation**: Return boolean success indicators

## Things to Avoid

- ❌ Direct instantiation → use `self.app.make(ServiceClass)`
- ❌ Sync methods in services → all service methods should be async
- ❌ Booting in `__init__` → use `boot()` for container-dependent initialization
- ❌ Broad exception catching → catch specific exceptions only
