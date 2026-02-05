---
name: documentation-convention
description: MkDocs structure, content organization, writing style, code examples, and maintenance practices for Byte documentation. Use when creating or updating documentation files, organizing content, or maintaining consistency across docs.
---

# Documentation Convention

## Structure & Organization

**MkDocs Material theme** - Configured in `mkdocs.yml`:

```yaml
theme:
  name: material
  features:
    - navigation.sections
    - navigation.indexes
    - content.code.copy
    - content.tabs.link
  palette:
    scheme: slate
    primary: black
```

**Three-tier navigation** - Introduction → Getting Started → Concepts → Reference:

```yaml
nav:
  - Introduction: index.md
  - Getting Started:
      - Overview: getting-started/index.md
      - Installation: getting-started/installation.md
  - Concepts:
      - concepts/index.md
      - File Context: concepts/file-context.md
  - References:
      - reference/index.md
      - Commands: reference/commands.md
```

**Index pages for sections** - Each directory has `index.md` with overview and navigation:

```markdown
# Getting Started

To help you get started with Byte, we'll cover a few important topics:

- [Installing Byte](installation.md)
- [First steps after installation](first-steps.md)

Read on, or jump ahead to another section:

- Learn more about the [core concepts](../concepts/index.md) in Byte
```

## Content Organization Patterns

**Start with overview paragraph** - Brief summary before horizontal rule:

```markdown
# File Context

The file context acts as the AI's "workspace" - only files added to the context are visible to the AI. This design gives you precise control over what the AI can access and change, preventing unwanted modifications and reducing noise in the AI's decision-making.

---
```

**Horizontal rules separate major sections** - Use `---` between top-level concepts:

```markdown
## Adding Files

[content]

---

## Viewing Context

[content]
```

**Progressive disclosure** - Start with quick start, then details:

```markdown
## Quick Start

Get started in three steps:

[minimal example]

---

## Why This Approach?

[detailed explanation]
```

**Related concepts at bottom** - Link to connected topics:

```markdown
## Related Concepts

- [File Watching](file-watching.md) - Automatic context updates
- [Conventions](conventions.md) - Project-specific guidelines
```

## Writing Style

**Second person for instructions** - "You" not "we" or "the user":

```markdown
# ✓ Good

You control exactly what context the LLM receives

# ✗ Bad

We control what context the LLM receives
The user controls what context the LLM receives
```

**Active voice** - Subject performs action:

```markdown
# ✓ Good

Byte automatically discovers all files in your project

# ✗ Bad

All files in your project are automatically discovered by Byte
```

**Short paragraphs** - 2-4 sentences maximum:

```markdown
The file context acts as the AI's "workspace" - only files added to the context are visible to the AI. This design gives you precise control over what the AI can access and change, preventing unwanted modifications and reducing noise in the AI's decision-making.

[New paragraph for new concept]
```

**Descriptive link text** - Not "click here":

```markdown
# ✓ Good

See the [Installation Guide](installation.md) for other methods

# ✗ Bad

Click [here](installation.md) for installation
```

**Bold for UI elements and first use** - Emphasize important terms:

```markdown
The **Read-Only Files** panel shows files available for reference.

On first run, Byte's `FirstBootService` will guide you through initial setup.
```

## Code Examples

**Shell prompts** - Use `$` for Unix commands:

````markdown
```bash
$ uv tool install byte-ai-cli
$ byte
```
````

````

**Minimal, runnable examples** - Show complete working code:
```markdown
```bash
# Install dependencies
uv sync

# Run commands in project environment
uv run byte
````

````

**Context before code** - Explain what the example demonstrates:
```markdown
Add individual files by specifying their path relative to the project root:

````

> /add src/services/auth.py
> /read-only README.md

```

```

**Language identifiers** - Always specify syntax highlighting:

````markdown
```yaml
files:
  ignore:
    - .byte/cache
    - "*.log"
```
````

````

**Command output examples** - Show expected results:
```markdown
````

> /add src/models/\*.py
> Added src/models/user.py (editable)
> Added src/models/post.py (editable)

```

```

**Inline code for commands and paths** - Use backticks:

```markdown
The discovery service builds an in-memory index of available files.

Export the `ANTHROPIC_API_KEY` environment variable.
```

## Admonitions

**Tip for helpful shortcuts** - Best practices and optimizations:

```markdown
!!! tip

    Before running Byte, you must have at least one of these environment variables set:
    `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY`.
```

**Note for additional context** - Supplementary information:

```markdown
!!! note

    The discovery service respects `.gitignore` patterns automatically.
```

**Warning for critical information** - Potential issues or requirements:

```markdown
!!! warning

    Changes require approval. Context additions need confirmation.
```

**Use sparingly** - Only when information truly needs emphasis.

## Visual Elements

**Screenshots with descriptive alt text** - Show UI state:

```markdown
![Byte Boot Screen](../images/boot.png)

![File context showing read-only and editable files](../images/recording/command_file.gif)
```

**Animated GIFs for workflows** - Demonstrate multi-step processes:

```markdown
<p align="center"><img width="800" alt="Byte Demo" src="https://raw.githubusercontent.com/usethefork/byte/main/docs/images/recording/example_coder.gif" /></p>
```

**Centered images for landing pages** - Use HTML for alignment:

```markdown
<p align="center"><img alt="Byte Logo" src="images/assets/logo.svg" /></p>
```

## Reference Documentation

**Auto-generated command reference** - Use scripts to maintain:

```markdown
## Files

### `/add`
```

usage: add file_path

Add file to context as editable

positional arguments:
file_path Path to file

```

```

**Grouped by category** - Organize commands logically:

```markdown
## System

## Agent

## Files

## Memory
```

**Configuration examples** - Show YAML structure:

```yaml
files:
  ignore:
    - .byte/cache
    - .ruff_cache
    - "*.log"
```

## Maintenance Practices

**Scripts for reference docs** - Auto-generate from code:

- `src/scripts/commands_to_md.py` → `docs/reference/commands.md`
- `src/scripts/settings_to_md.py` → `docs/reference/settings.md`

**Validation in mkdocs.yml** - Catch broken links:

```yaml
validation:
  omitted_files: warn
  absolute_links: warn
  unrecognized_links: warn
```

**Prettier for markdown** - Consistent formatting:

```bash
prettier --write docs/**/*.md
```

**Update examples when code changes** - Keep docs synchronized with implementation.

**Test code examples** - Verify all commands and code blocks work.

## Best Practices

**Start with "Getting Started"** - New users need quick wins first.

**Provide working examples before API docs** - Show usage before reference.

**Include real-world use cases** - Not just syntax documentation.

**Keep line length readable** - 80-100 chars for markdown source.

**Use relative paths for internal links** - Portable across environments:

```markdown
See the [Installation Guide](getting-started/installation.md)
```

**Progressive complexity** - Simple examples first, advanced features later.

**Cross-reference related concepts** - Help users discover connected features.
