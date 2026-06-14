# Configure Linting

**Category**: How-to Guide

This guide shows you how to set up and use linting in Byte. You'll learn how to enable linting, configure lint commands, run linting manually, and let the Coder Agent automatically fix lint errors during workflows.

## Prerequisites

- Byte installed on your system
- Basic understanding of your project's linting tools (Ruff, Prettier, ESLint, etc.)
- A `.byte/config.jsonc` file (created during initialization)

## Step 1: Enable Linting

Linting is disabled by default. To enable it, open `.byte/config.jsonc` and add or update the `lint` section:

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [],
  },
}
```

Setting `enable: true` activates linting. The `commands` array is where you define which linters to run.

## Step 2: Add Lint Commands

Each command in the `commands` array specifies a linting tool and which file types it should check. Add entries like this:

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [
      {
        "command": ["ruff", "check", "--fix", "{file}"],
        "languages": ["python"],
      },
      {
        "command": ["ruff", "format", "{file}"],
        "languages": ["python"],
      },
      {
        "command": ["prettier", "--write", "{file}"],
        "languages": ["javascript", "typescript", "json"],
      },
    ],
  },
}
```

Each command has two required fields:

- **`command`** — An array of strings representing the full command to run. Use `{file}` as a placeholder for the file path; Byte replaces it with the actual file being linted. If you don't use `{file}`, the file path is appended to the end of the command.
- **`languages`** — An array of language names this command handles. Byte determines file language using file extension. Use `["*"]` to run the command on all files regardless of language.

### Example: Ruff for Python

```jsonc
{
  "command": ["ruff", "check", "--fix"],
  "languages": ["python"],
}
```

This runs `ruff check --fix` on all Python files. Since there's no `{file}` placeholder, the file path is appended automatically.

### Example: Prettier for Multiple Languages

```jsonc
{
  "command": ["prettier", "--write", "{file}"],
  "languages": ["javascript", "typescript", "jsx", "json", "yaml"],
}
```

This runs Prettier with the `{file}` placeholder explicitly positioned.

### Example: Linter That Handles All Files

```jsonc
{
  "command": ["shellcheck", "{file}"],
  "languages": ["*"],
}
```

This runs ShellCheck on all files.

## Step 3: Understand When Linting Runs

Linting runs in two contexts:

### During `/coder` Workflow

When you use `/coder` to make code changes, linting runs automatically as a phase if enabled. The Coder Agent:

1. Makes the requested code changes
2. Runs linters on the modified files
3. If lint errors appear, automatically fixes them and re-runs linting
4. Repeats until all lint errors are resolved
5. Completes the workflow

You don't need to do anything—linting happens as part of the workflow.

### Using the `/lint` Command

You can also run linting independently:

```bash
/lint
```

This command:

1. Runs all configured lint commands on files you've changed in git (tracked files with uncommitted changes)
2. Displays any lint errors found
3. Prompts you: "Attempt to fix lint errors?"
   - If you say **yes**, the Coder Agent launches to fix the errors automatically
   - If you say **no**, the errors are reported but no fixes are applied

## Step 4: Configure Lint Commands for Your Project

Different projects need different linters. Here are common setups:

### Python Projects (Ruff)

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [
      {
        "command": ["ruff", "check", "--fix"],
        "languages": ["python"],
      },
      {
        "command": ["ruff", "format"],
        "languages": ["python"],
      },
    ],
  },
}
```

### JavaScript / TypeScript (ESLint + Prettier)

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [
      {
        "command": ["eslint", "--fix", "{file}"],
        "languages": ["javascript", "typescript", "jsx", "tsx"],
      },
      {
        "command": ["prettier", "--write", "{file}"],
        "languages": ["javascript", "typescript", "json", "yaml"],
      },
    ],
  },
}
```

### Go Projects

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [
      {
        "command": ["gofmt", "-w", "{file}"],
        "languages": ["go"],
      },
      {
        "command": ["golangci-lint", "run", "--fix", "{file}"],
        "languages": ["go"],
      },
    ],
  },
}
```

### Mixed (Python + JavaScript)

```jsonc
{
  "lint": {
    "enable": true,
    "commands": [
      {
        "command": ["ruff", "check", "--fix"],
        "languages": ["python"],
      },
      {
        "command": ["eslint", "--fix", "{file}"],
        "languages": ["javascript", "typescript"],
      },
      {
        "command": ["prettier", "--write", "{file}"],
        "languages": ["javascript", "typescript", "json"],
      },
    ],
  },
}
```

## Step 5: Test Your Lint Configuration

Make a small, deliberate change to a file that triggers a lint error:

```bash
# Add a long line or unused variable to a Python file, for example
```

Then run:

```bash
/lint
```

If linting works, you'll see the errors reported. If you say yes to auto-fix, the Coder Agent will correct them.

## Step 6: Understand File Targeting

Linting only runs on files that were actually modified:

- **In `/coder` workflow** — Only files touched during the workflow are linted
- **With `/lint` command** — Only files with uncommitted changes in git are linted

This keeps linting fast by avoiding unnecessary checks on unrelated files.

## Next Steps

Now that linting is configured, use `/coder` or `/lint` to make code changes with automatic validation. Linting catches issues early and ensures code quality throughout your project.
