# Manage File Context

**Category**: How-to Guide

File context lets you surface files that Byte can't normally access. By default, Byte ignores directories like `.venv`, `vendor`, `node_modules`, and other ignored paths — files in those directories are invisible to its normal operations. File context is the tool to bring those hidden files into view. Add a library's source code from `.venv`, check a vendored dependency, or inspect external code that would otherwise stay out of reach.

## Prerequisites

- Byte installed on your system
- A file outside your normal project scope (in an ignored directory or external location) you want to add to context

## Step 1: Understand Session Context

Session context is temporary storage for files and web pages that persist only for the current session. It's specifically designed for files Byte wouldn't normally see because they're in ignored directories or outside your project scope. When you add a file to context:

1. Byte reads the file from disk
2. Stores it as markdown in `.byte/session_context/`
3. Injects it into the AI's prompt before every response
4. Tags it with `type="file"` for tracking

When you end your session, context files are kept on disk but not actively used. Starting a new session gives you a fresh context.

## Step 2: Add a Hidden File with `/context`

The simplest way to add a file is the smart `/context` command, which auto-detects whether you're adding a file or URL:

```bash
/context .venv/lib/python3.12/site-packages/requests/api.py
```

This command:

1. Detects that the path is a file (not a URL)
2. Reads the file from disk — even if it's in an ignored directory
3. Adds it to context with the file path as the context key
4. Confirms: "Added .venv/lib/python3.12/site-packages/requests/api.py to session context"

You can add any file type: Python, JSON, YAML, markdown, etc. — regardless of where it lives on disk.

### Example: Add Multiple Hidden Files One by One

```bash
/context vendor/package/src/core.py
/context .venv/lib/python3.12/site-packages/numpy/__init__.py
/context node_modules/lodash/index.js
```

Each file is added separately and appears in your context. These are files Byte can't normally access; now they're visible to the AI.

## Step 3: Add a File Directly with `/ctx:file`

For explicit file operations, use the direct `/ctx:file` command:

```bash
/ctx:file .venv/lib/python3.12/site-packages/urllib3/request.py
```

This is identical to `/context` for files — it reads the file and adds it to context. Use this when you want to be explicit, or when the smart detection might mistake your input.

### Relative Paths

Both `/context` and `/ctx:file` accept relative paths and resolve them from your project root:

```bash
/context .venv/lib/python3.12/site-packages/flask/app.py
/context ./vendor/lib/utils.py
```

### Error Handling

If the file doesn't exist:

```
Error: File not found: .venv/lib/python3.12/site-packages/missing.py
```

If the path is a directory instead of a file:

```
Error: Path is not a file: .venv/lib/python3.12/site-packages/
```

## Step 4: List All Context Items

View everything currently in your session context:

```bash
/ctx:ls
```

Output shows all items by key in a formatted panel:

```
╭────────────────────────────────────────╮
│ Session Context Items (3)              │
├────────────────────────────────────────┤
│ .venv/.../requests/api.py              │
│ vendor/package/src/core.py             │
│ node_modules/lodash/index.js           │
╰────────────────────────────────────────╯
```

The keys match the file paths you added. Use these keys to remove items (see Step 5).

## Step 5: Remove Context Items

Remove individual items or multiple items at once.

### Remove a Specific Item by Key

If you know the key, remove it directly:

```bash
/ctx:drop .venv/lib/python3.12/site-packages/requests/api.py
```

Byte confirms: "Removed .venv/lib/python3.12/site-packages/requests/api.py from session context"

### Remove Multiple Items Interactively

Call `/ctx:drop` without a key to open a multi-select menu:

```bash
/ctx:drop
```

A menu appears:

```
? Select context items to drop

❯ ◻ .venv/lib/python3.12/site-packages/requests/api.py
  ◻ vendor/package/src/core.py
  ◻ node_modules/lodash/index.js
```

Use arrow keys to navigate and spacebar to select multiple items. Press Enter when done.

Byte confirms: "Removed 2 items from session context"

### Why Remove Items?

Context takes up tokens in your AI conversation. Remove files you've finished referencing to keep context lean and focused.

## Step 6: How Context Reaches the AI

When you send a message, Byte automatically injects all context items into the AI's prompt before sending it. Each file is wrapped with metadata tags:

```
<session_context type="file" key=".venv/lib/python3.12/site-packages/requests/api.py">
[file contents here]
</session_context>
```

The AI can see all files in context and reference them by key. You don't need to manually include files in your prompt — they're always available.

## Step 7: Understand Persistence

**Session persistence:** Context files live in `.byte/session_context/` on your disk. They persist across prompts within the same session.

**Session boundaries:** When you end your session and start a fresh one, context is cleared. You need to re-add files if you want them in the new session.

To start fresh immediately:

```bash
/ctx:drop
# Select all items and confirm removal
```

Then add what you need for the current task.

## Common Workflows

### Understanding a Vendored Dependency

Add the vendored library source code to understand its API:

```bash
/context vendor/lib/special-math/src/algorithm.py
/context vendor/lib/special-math/src/utils.py
```

Ask the AI how to use the library, what functions are available, or how to integrate it. The AI can examine the actual source code.

### Debugging with .venv Sources

Add the source from an installed package to debug integration issues:

```bash
/context .venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py
/context .venv/lib/python3.12/site-packages/sqlalchemy/orm/query.py
```

Describe the issue. The AI can see the library's actual implementation and help you troubleshoot.

### Analyzing External Libraries

Add source files from dependencies to understand behavior:

```bash
/context .venv/lib/python3.12/site-packages/pydantic/main.py
/context .venv/lib/python3.12/site-packages/pydantic/validators.py
```

Ask the AI questions about validation, configuration, or performance. It can read the actual library code.

### Inspecting Node Modules

For JavaScript/Node projects, add JavaScript library source:

```bash
/context node_modules/express/lib/express.js
/context node_modules/express/lib/middleware/router.js
```

Ask the AI how the framework works or how to extend it. The AI has the real source in view.

## Combining File and Web Context

You can mix file context with web context (see the web context guide). Add files from ignored directories for your codebase, add web pages for external documentation:

```bash
/context .venv/lib/python3.12/site-packages/requests/api.py
/context https://docs.example.com/api
/ctx:ls  # Shows both types
```

Both are injected together when you send a message.

## Next Steps

Now that you can manage file context, explore web context to add external documentation and resources. For advanced context workflows, see the explanation section on how context is structured and prioritized.
