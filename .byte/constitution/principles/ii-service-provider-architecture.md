---
name: II. Service Provider Architecture
---

All domain functionality MUST be encapsulated in service providers registered through the application container. Direct instantiation of services outside the DI container is prohibited. Services MUST resolve dependencies via `self.app.make()` or container access patterns. New domains MUST include a `service_provider.py` that registers all services, commands, and bindings during the boot lifecycle. Rationale: Consistent dependency resolution ensures testability, modularity, and predictable boot sequencing.
