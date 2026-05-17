---
name: III. Domain Isolation
---

Each functional domain (e.g., git, files, llm, lint, parsing, constitution) MUST be self-contained with its own service provider, commands, services, and schemas. Cross-domain dependencies MUST flow through the application container never via direct imports of another domain's internal services. Each domain directory MUST follow the established structure: `__init__.py`, `service_provider.py`, `command/`, `service/`, and optionally `schemas.py`, `models.py`, or `tools/`.

Rationale: Prevents coupling and enables independent evolution of domains.
