# Byte Architecture Guide

Byte is a CLI AI assistant built with **Domain-Driven Design**, **Dependency Injection**, and **Event-Driven Architecture**.

## Core Patterns

- **Service Provider Pattern**: Two-phase initialization (register → boot)
- **Command Pattern**: User interactions via `/command` syntax
- **Event-Driven**: Cross-domain communication via domain events
- **Mixin Auto-Boot**: Mixins initialize via `boot_{mixin_name}` methods
- **Configuration System**: Layered config (YAML → env vars → CLI args)

## Project Structure

```
byte/
├── core/                    # Framework infrastructure
│   ├── command/            # Command pattern & registry
│   ├── config/             # Configuration system
│   ├── events/             # Event system (Observer pattern)
│   └── ui/                 # User interface components
├── domain/                 # Business logic domains
│   ├── files/              # File context management
│   ├── commit/             # Git commit functionality
│   ├── llm/                # Language model integration
│   └── system/             # Core system commands
├── container.py            # Dependency injection
├── bootstrap.py            # Application initialization
└── main.py                 # CLI entry point
```

## Key Components

### Container (`container.py`)
Simple DI container with singleton/transient lifetimes.

### Configuration (`core/config/`)
Layered config system: `.byte/config.yaml` → env vars → CLI args.

### Commands (`core/command/`)
Command pattern with auto-completion and mixin support.

### Events (`core/events/`)
Observer pattern for loose coupling between domains.

### LLM Integration (`domain/llm/`)
Provider-agnostic AI with auto-detection (Anthropic → OpenAI → Gemini).

## Initialization Flow

1. **Bootstrap** registers service providers
2. **Register Phase** - Bind services to container
3. **Boot Phase** - Configure relationships
4. **Main Loop** - Process user commands

## Extension Points

- **Commands**: Extend `Command` + mixins (auto-boot)
- **Domains**: Add service provider + events
- **LLM Providers**: Implement `LLMService` interface
- **Config**: Add to schema + service mappings

## Best Practices

- Type hints for all public interfaces
- Document with purpose + usage examples
- Use events for cross-domain communication
- Immutable data structures (`@dataclass(frozen=True)`)
- Follow [Python Style Guide](PYTHON_STYLEGUIDE.md) and [Comment Style Guide](COMMENT_STYLEGUIDE.md)
