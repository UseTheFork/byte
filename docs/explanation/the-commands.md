# The Commands

**Category**: Explanation

Commands are the primary way you interact with Byte. Type a slash command in the CLI and the agent executes it immediately—no delays, no configuration. Commands handle everything from adding files to context to running AI workflows to managing your project's specification. They're fast, focused, and designed to fit naturally into your development flow.

## What Is a Command?

A command is a single action you invoke by typing a slash (`/`) followed by the command name and optional arguments. Each command performs a specific task: `/add myfile.py` adds a file to context, `/coder "implement feature X"` asks the AI to code something, `/lint` runs linting checks.

Commands are not scripts or macros. They're discrete, atomic operations. The command completes, and you immediately see the result. If the command invokes an AI workflow, streaming output flows back to you in real time.

## How Commands Work

### Invocation

Type a slash and the command name in the Byte CLI prompt:

```
> /add src/main.py
```

Some commands accept arguments:

```
> /coder refactor this function to use async/await
```

Others use subcommands (colon-separated):

```
> /spec:init --design-exploration
```

The parser splits your input, the command registry looks up the handler, and the command executes. If parsing fails, Byte shows you the usage error immediately.

### Categories

Commands are grouped by category to help you discover what you need:

- **Agent** — Commands that invoke AI workflows: code generation, specifications, commits, linting, constitution edits, skills, projects.
- **Context** — Commands that manage what the AI sees: adding files, dropping context, listing current context.
- **File Management** — Commands that add or remove files from the AI's editable context.

### Discovery

You can list all available commands directly in the Byte CLI. Type `/help` or use tab completion to see what's available. Each command includes a description and category.

### Integration with Workflows

Commands don't exist in isolation. Many commands trigger AI workflows. For example, `/spec:init` creates a thorough specification, which internally coordinates with the LLM, writes output files, and manages phases. `/coder` invokes the coder workflow, which breaks your request into planning, implementation, and validation steps.

When a command starts a workflow, you see streaming output as the workflow progresses. Workflows are stateful and track phases—you know exactly where you are in the process.

## The Protocol

Byte's command system is built around the `Command` interface. Each command:

1. **Has a name** — Slug-style identifier for invocation (`add`, `coder`, `spec:init`)
2. **Has a category** — Logical grouping for discovery and documentation
3. **Has a description** — Human-readable explanation of what it does
4. **Defines arguments** — What parameters the command accepts (if any)
5. **Executes asynchronously** — Non-blocking, real-time feedback to the user

The command registry maintains a central dispatch table. When you type a command, the registry routes it to the handler. Tab completion delegates to individual command handlers for context-aware suggestions.

## Available Commands

The complete list of available commands and their detailed usage is documented on the [Available Commands](available-commands.md) subpage. Commands are organized by category for quick lookup.

