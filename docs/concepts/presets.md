# Presets

Presets allow you to save and quickly load predefined configurations of files, conventions, and prompts. They're ideal for switching between different workflows, project contexts, or documentation tasks without manually adding files each time.

![Preset loading process](../images/presets.png)

---

## Quick Start

Load a preset configuration:

```
> /preset command
```

Byte will:

1. Prompt to clear conversation history (optional)
2. Prompt to clear current file context (optional)
3. Add configured read-only files to context
4. Add configured editable files to context
5. Load specified conventions
6. Set a default prompt (if configured)

---

## Configuration

Define presets in `.byte/config.yaml`:

```yaml
presets:
  - id: command
    conventions:
      - CODE_STYLEGUIDE.md
      - PROJECT_ARCHITECTURE.md
    read_only_files:
      - src/byte/bootstrap.py
      - src/byte/container.py
    editable_files:
      - src/byte/domain/cli/command/new_command.py
    prompt: "Create a new command following the existing patterns"
    load_on_boot: false
```

### Configuration Options

For complete configuration details, see the [Settings Reference](../reference/settings.md#presets).

**`id`** (string, required)

- Unique identifier used in `/preset <id>` command
- Use descriptive names like "command", "docs", or "testing"

**`read_only_files`** (array of strings, default: `[]`)

- Files to add as read-only context
- Supports glob patterns like `src/**/*.py`
- Files are visible to AI but cannot be modified

**`editable_files`** (array of strings, default: `[]`)

- Files to add as editable context
- Supports glob patterns
- AI can propose changes to these files

**`conventions`** (array of strings, default: `[]`)

- Convention files to load from `.byte/conventions/`
- Provide coding standards and style guides to the AI

**`prompt`** (string, optional)

- Default prompt text to populate the input field
- Useful for repetitive tasks with similar instructions

**`load_on_boot`** (boolean, default: `false`)

- Automatically load this preset when Byte starts
- Only one preset should have this enabled

---

## Common Use Cases

### Command Development

Create a preset for building new CLI commands:

```yaml
presets:
  - id: command
    conventions:
      - CODE_STYLEGUIDE.md
      - PROJECT_ARCHITECTURE.md
    read_only_files:
      - src/byte/domain/cli/service/command_registry.py
      - src/byte/core/mixins/user_interactive.py
    editable_files:
      - src/byte/domain/*/command/*.py
```

Load it when working on commands:

```
> /preset command
```

### Documentation Writing

Set up a preset for documentation tasks:

```yaml
presets:
  - id: mkdocs
    conventions:
      - MKDOCS_STYLEGUIDE.md
    read_only_files:
      - docs/concepts/file-context.md
      - docs/concepts/lint.md
    editable_files:
      - docs/concepts/new-feature.md
    prompt: "Using the MKDOCS_STYLEGUIDE and existing docs as examples, document "
```

The preset includes example docs as reference and sets a helpful default prompt.

### Testing Workflow

Configure a preset for test development:

```yaml
presets:
  - id: testing
    conventions:
      - TESTING_STYLEGUIDE.md
    read_only_files:
      - src/byte/domain/*/service/*.py
    editable_files:
      - tests/**/*_test.py
    prompt: "Write tests for "
```

---

## Workflow Integration

### History Management

When loading a preset, you can optionally clear conversation history:

```
Would you like to clear the conversation history before loading this preset? (Y/n):
```

Choose **Yes** to start fresh with the new context, or **No** to preserve previous conversation while switching files.

### Context Management

You can also clear the current file context:

```
Would you like to clear the file context before loading this preset? (y/N):
```

Choose **Yes** to replace all files with the preset configuration, or **No** to add preset files to existing context.

### Auto-Loading

Set `load_on_boot: true` to automatically load a preset when Byte starts:

```yaml
presets:
  - id: default
    load_on_boot: true
    editable_files:
      - src/**/*.py
```

This is useful for projects where you always work with the same initial context.

---

## Related Concepts

- [File Context](file-context.md) - Understanding file modes and context management
- [Conventions](conventions.md) - Project-specific coding standards
- [Settings Reference](../reference/settings.md) - Complete configuration options
