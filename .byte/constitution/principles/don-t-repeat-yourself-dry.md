---
id: don-t-repeat-yourself-dry
name: Don't Repeat Yourself (DRY)
order: 20
---
All code MUST avoid unnecessary duplication of logic, configuration, and data definitions. Shared behavior MUST be extracted into reusable services, utilities, or base classes and resolved through the application container or established import patterns. When identical or near-identical logic exists in more than one location, it MUST be consolidated into a single authoritative source. Duplication in test fixtures, schema definitions, and prompt templates MUST be reduced through shared factories, constants, or helper modules. Shared logic MUST be extracted into `src/byte/support/`.
