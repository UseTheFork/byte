# Linting

Byte's linting system automatically runs configured code quality tools on your files to identify and fix issues. It integrates seamlessly with your workflow, running linters on changed files or specific contexts with a simple command.

![Lint process showing progress and results](../images/commit_lint.png)

---

## Quick Start

Run linters on all changed files:

```
> /lint
```

Byte will:

1. Stage your current changes with git
2. Identify files modified since last commit
3. Run configured linters based on file extensions
4. Display results with error details
5. Optionally attempt AI-assisted fixes for errors

---

## Configuration

Configure linters in `.byte/config.yaml`:

```yaml
lint:
  enable: true
  commands:
    - command: "uv run ruff format --force-exclude --respect-gitignore"
      extensions: [".py"]
    - command: "uv run ruff check --fix --force-exclude"
      extensions: [".py"]
    - command: "prettier --write"
      extensions: [".md"]
    - command: "keep-sorted"
      extensions: ["*"]
```

### Configuration Options

For complete configuration details, see the [Settings Reference](../reference/settings.md#lint).

**`lint.enable`** (boolean, default: `true`)

- Enable or disable the linting functionality entirely

**`lint.commands`** (array)

- List of lint commands to execute

Each command object has:

**`command`** (string, required)

- The shell command to execute (e.g., `"ruff check --fix"`)
- Command runs from project root directory
- Use full paths or ensure tools are in PATH

**`extensions`** (array of strings, required)

- File extensions this command applies to (e.g., `[".py", ".pyi"]`)
- Use `["*"]` to run on all files regardless of extension
- Match is done on file suffix

---

## How It Works

For each lint command:

1. **Filter Files** - Select files matching the command's extensions
2. **Build Commands** - Construct full command: `{command} {file_path}`
3. **Execute Async** - Run commands concurrently for performance
4. **Capture Output** - Collect stdout, stderr, and exit codes
5. **Report Results** - Display summary with errors and warnings

---

## AI-Assisted Fixes

When lint errors are found, Byte can attempt automated fixes:

```
Attempt to fix lint errors? (y/N):
```

If you confirm:

1. **Coder Agent** - Byte invokes the coder agent for each file
2. **Error Context** - Provides the lint error message and file path
3. **Suggested Fix** - AI proposes SEARCH/REPLACE blocks to resolve the issue
4. **Review** - You review and approve the changes

This is particularly useful for:

- Formatting issues the linter couldn't auto-fix
- Complex refactoring suggested by linters
- Understanding why a lint rule failed

### Order Matters

Run formatters before linters:

```yaml
commands:
  - command: "ruff format" # Format first
    extensions: [".py"]
  - command: "ruff check --fix" # Then check
    extensions: [".py"]
```

This prevents formatters from introducing new lint errors.

### Keep Commands Fast

Use caching and incremental modes:

```yaml
- command: "mypy --cache-dir=.mypy_cache"
  extensions: [".py"]
```
