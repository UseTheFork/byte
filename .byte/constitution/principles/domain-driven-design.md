---
id: domain-driven-design
name: Domain Driven Design
order: 10
---
All business logic MUST be organized into bounded-context domains under `src/byte/`. Cross-domain communication MUST occur through explicit public interfaces — never by reaching into another domain's internals. New features MUST be placed in the appropriate existing domain or justify the creation of a new one.
